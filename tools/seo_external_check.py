#!/usr/bin/env python3
"""External SEO checks on the LIVE site (run by .github/workflows/seo-external-check.yml).

  * Google PageSpeed Insights (Lighthouse, mobile + desktop): performance,
    accessibility, best practices, SEO scores + Core Web Vitals lab values
  * W3C Nu HTML Checker: errors / warnings per page
  * Schema.org validator (validator.schema.org): structured-data objects + errors
  * robots.txt / sitemap.xml reachable from the main domain

Prints a JSON report between SEO-CHECK-BEGIN / SEO-CHECK-END. Nothing is committed.
Google's Rich Results Test has no public API, so it stays a manual check.
"""
import json
import os
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

SITE = "https://drmilladmikhail.com"
PAGES = ["/", "/about/", "/about/qualifications/", "/about/publications/", "/family/", "/en/about/",
         "/articles/couples-counseling/", "/book/", "/sessions/", "/tests/"]
PSI_PAGES = ["/", "/about/", "/articles/couples-counseling/"]
UA = {"User-Agent": "Mozilla/5.0 drmilladmikhail-seo-check"}


def get(url, data=None, headers=None, timeout=120):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:500]
    except Exception as e:
        return 0, str(e)[:300]


def psi(path, strategy):
    local = lighthouse_local(path, strategy)
    if local:
        return local
    q = urllib.parse.urlencode([("url", SITE + path), ("strategy", strategy)] +
                               [("category", c) for c in ("performance", "accessibility", "best-practices", "seo")])
    st, body = get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + q, timeout=180)
    if st != 200:
        return {"error": st, "detail": body[:200]}
    return summarise(json.loads(body)["lighthouseResult"], "PageSpeed Insights")


def lighthouse_local(path, strategy):
    """Fallback when the PageSpeed API is out of quota: Lighthouse run on the runner
    by the workflow (same engine Google uses), JSON files in $LH_DIR."""
    name = (path.strip("/").replace("/", "_") or "home") + "-" + strategy + ".json"
    f = os.path.join(os.environ.get("LH_DIR", "/tmp/lh"), name)
    if not os.path.exists(f):
        return None
    try:
        return summarise(json.load(open(f, encoding="utf-8")), "Lighthouse on GitHub runner")
    except Exception as e:
        return {"error": "lighthouse-unparsed", "detail": str(e)[:200]}


def summarise(d, source):
    cats = {k: round(v["score"] * 100) if v.get("score") is not None else None for k, v in d["categories"].items()}
    a = d["audits"]
    pick = lambda k: a.get(k, {}).get("displayValue")
    failing_seo = [a[r["id"]]["title"] for r in d["categories"]["seo"]["auditRefs"]
                   if r.get("weight") and a.get(r["id"], {}).get("score") not in (1, None)]
    shifts = []
    for it in (a.get("layout-shifts", {}).get("details") or {}).get("items", [])[:4]:
        node = it.get("node") or {}
        causes = [c.get("extra", {}).get("value") or c.get("cause") for c in
                  ((it.get("subItems") or {}).get("items") or [])]
        shifts.append({"score": round(it.get("score", 0), 3), "el": (node.get("selector") or node.get("snippet") or "")[:90],
                       "causes": [str(c)[:90] for c in causes if c][:3]})
    return {"source": source, "scores": cats, "shifts": shifts, "LCP": pick("largest-contentful-paint"), "CLS": pick("cumulative-layout-shift"),
            "TBT": pick("total-blocking-time"), "FCP": pick("first-contentful-paint"), "SI": pick("speed-index"),
            "seo_failing": failing_seo}


VNU = os.environ.get("VNU_JAR", "")


def w3c(path):
    """W3C Nu checker. The same checker the W3C site runs (vnu.jar), run on the runner
    against the live page's HTML, because validator.w3.org rate-limits (429) after a few pages."""
    st, html = get(SITE + path)
    if st != 200:
        return {"error": st}
    if VNU and os.path.exists(VNU):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(html)
        out = subprocess.run(["java", "-jar", VNU, "--format", "json", f.name],
                             capture_output=True, text=True, timeout=300).stderr
        os.unlink(f.name)
        line = next((l for l in out.splitlines() if l.startswith('{"messages"')), '{"messages":[]}')
        msgs, source = json.loads(line).get("messages", []), "vnu.jar on runner"
    else:
        st, body = get("https://validator.w3.org/nu/?" + urllib.parse.urlencode({"doc": SITE + path, "out": "json"}))
        if st != 200:
            return {"error": st}
        msgs, source = json.loads(body).get("messages", []), "validator.w3.org"
    errs = [m for m in msgs if m.get("type") == "error"]
    warns = [m for m in msgs if m.get("subType") == "warning"]
    return {"source": source, "errors": len(errs), "warnings": len(warns),
            "first_errors": sorted({m.get("message", "")[:140] for m in errs})[:6]}


def schema(path):
    data = urllib.parse.urlencode({"url": SITE + path}).encode()
    st, body = get("https://validator.schema.org/validate", data=data,
                   headers={"Content-Type": "application/x-www-form-urlencoded"})
    if st != 200:
        return {"error": st}
    body = body[body.find("{"):]
    try:
        d = json.loads(body)
    except ValueError:
        return {"error": "unparsed"}
    types = sorted({t.get("type") or "?" for t in d.get("tripleGroups", [])}) if isinstance(d.get("tripleGroups"), list) else []
    return {"objects": d.get("numObjects"), "errors": d.get("totalNumErrors"), "warnings": d.get("totalNumWarnings"),
            "types": types}


def main():
    rep = {"basics": {}, "pagespeed": {}, "w3c": {}, "schema": {}}
    for f in ("/robots.txt", "/sitemap.xml", "/llms.txt"):
        st, body = get(SITE + f)
        rep["basics"][f] = {"status": st, "bytes": len(body)}
    for p in PSI_PAGES:
        for s in ("mobile", "desktop"):
            rep["pagespeed"][f"{p} {s}"] = psi(p, s)
    for p in PAGES:
        rep["w3c"][p] = w3c(p)
        time.sleep(1)
        rep["schema"][p] = schema(p)
    print("SEO-CHECK-BEGIN")
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    print("SEO-CHECK-END")


if __name__ == "__main__":
    main()
