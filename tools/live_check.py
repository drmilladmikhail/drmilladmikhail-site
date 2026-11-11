#!/usr/bin/env python3
"""Check the LIVE site (https://drmilladmikhail.com) in a real browser.

Run by .github/workflows/live-check.yml (manual). Prints a JSON report between
LIVE-CHECK-BEGIN / LIVE-CHECK-END in the job log. Nothing is committed.

What it checks, for every page in the live sitemap (+ /en/ and the 404 page):
  * the page loads (HTTP 200) on phone (390px) and desktop (1280px), light + dark
  * JavaScript errors, blocked requests (Content-Security-Policy), missing files
  * horizontal overflow on phones
  * accessibility (axe-core, WCAG 2.1 AA + best practice)
  * every internal link / image / script / stylesheet answers 200
  * external links (warnings only: some sites block robots)
  * the live copy matches this commit (assets are byte-identical)
  * redirects: http -> https, www -> apex
The Cloudflare analytics beacon is blocked so the check does not count as visits.
"""
import concurrent.futures as cf
import os
import hashlib
import json
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

SITE = os.environ.get("LIVE_SITE", "https://drmilladmikhail.com")
ROOT = Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36 drmilladmikhail-live-check"
AXE = sys.argv[1] if len(sys.argv) > 1 else "node_modules/axe-core/axe.min.js"


def fetch(url, method="GET", follow=True):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=25) as r:
            return r.status, r.geturl(), (r.read() if method == "GET" else b"")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location") or url, b""
    except Exception as e:  # network error
        return 0, str(e)[:120], b""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("href", "src", "poster"):
            if a.get(k) and not (tag == "link" and a.get("rel") in ("preconnect", "dns-prefetch")):
                self.refs.append(a[k])
        if a.get("srcset"):
            self.refs += [p.strip().split(" ")[0] for p in a["srcset"].split(",") if p.strip()]


def main():
    report = {"pages": [], "broken_internal": [], "external_warnings": [], "stale_assets": [],
              "redirects": {}, "summary": {}}

    # 1. redirects
    for src in ("http://drmilladmikhail.com/", "https://www.drmilladmikhail.com/", "http://www.drmilladmikhail.com/"):
        st, final, _ = fetch(src)
        report["redirects"][src] = {"status": st, "final": final, "ok": st == 200 and final.rstrip("/") == SITE}

    # 2. page list from the live sitemap
    st, _, body = fetch(SITE + "/sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [n.text.strip() for n in ET.fromstring(body).findall(".//s:loc", ns)] if st == 200 else []
    for extra in (SITE + "/", SITE + "/en/"):
        if extra not in urls:
            urls.append(extra)
    urls = urls[:int(os.environ.get("LIVE_LIMIT", "100000"))]
    report["summary"]["sitemap_status"] = st
    report["summary"]["pages"] = len(urls)

    # 3. live assets == this commit
    for f in sorted((ROOT / "assets").glob("*.*")):
        if f.suffix not in (".js", ".css"):
            continue
        st, _, live = fetch(SITE + "/assets/" + f.name)
        if st != 200 or hashlib.sha256(live).digest() != hashlib.sha256(f.read_bytes()).digest():
            report["stale_assets"].append({"file": f.name, "status": st})

    # 4. collect every reference from every page's HTML
    html_cache, refs = {}, {}
    def get_html(u):
        return u, fetch(u)
    with cf.ThreadPoolExecutor(8) as ex:
        for u, (st, final, body) in ex.map(get_html, urls):
            html_cache[u] = st
            if st != 200:
                continue
            p = Refs()
            p.feed(body.decode("utf-8", "replace"))
            for r in p.refs:
                if r.startswith(("mailto:", "tel:", "javascript:", "data:", "#", "whatsapp:", "sms:")):
                    continue
                full = urldefrag(urljoin(u, r))[0]
                refs.setdefault(full, set()).add(u.replace(SITE, ""))

    def check(u):
        host = urlparse(u).netloc
        st, final, _ = fetch(u, "GET" if host.endswith("drmilladmikhail.com") else "GET")
        return u, st
    with cf.ThreadPoolExecutor(12) as ex:
        for u, st in ex.map(check, sorted(refs)):
            if st == 200:
                continue
            item = {"url": u, "status": st, "on": sorted(refs[u])[:4]}
            if urlparse(u).netloc == "drmilladmikhail.com":
                report["broken_internal"].append(item)
            elif st not in (401, 403, 405, 429, 999):
                report["external_warnings"].append(item)
    report["summary"]["links_checked"] = len(refs)

    # 5. real browser
    from playwright.sync_api import sync_playwright
    axe_src = Path(AXE).read_text()
    combos = [((390, 844), "light"), ((390, 844), "dark"), ((1280, 900), "light"), ((1280, 900), "dark")]
    targets = urls + [SITE + "/this-page-does-not-exist-check/"]
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for (w, h), scheme in combos:
            ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme, user_agent=UA)
            ctx.add_init_script(axe_src)
            ctx.route("**/*", lambda r: r.abort() if "cloudflareinsights.com" in r.request.url else r.continue_())
            for u in targets:
                pg = ctx.new_page()
                errs = []
                pg.on("pageerror", lambda e: errs.append("js: " + str(e)[:220]))
                pg.on("console", lambda m: errs.append("console: " + m.text[:220])
                      if m.type == "error" and "cloudflareinsights" not in m.text and "ERR_FAILED" not in m.text else None)
                pg.on("response", lambda r: errs.append(f"http {r.status}: {r.url}")
                      if r.status >= 400 and "drmilladmikhail.com" in r.url and "does-not-exist" not in r.url else None)
                entry = {"url": u.replace(SITE, "") or "/", "view": f"{w}-{scheme}"}
                try:
                    resp = pg.goto(u, wait_until="load", timeout=45000)
                    entry["status"] = resp.status if resp else 0
                    pg.wait_for_timeout(600)
                    entry["overflow"] = pg.evaluate("""() => {
                      const W = document.documentElement.clientWidth, out = [];
                      if (document.documentElement.scrollWidth > W + 1) out.push('page ' + document.documentElement.scrollWidth + 'px');
                      return out; }""")
                    entry["errors"] = sorted(set(errs))
                    entry["axe"] = pg.evaluate("""async () => {
                      if (!window.axe) return ['axe not loaded'];
                      const r = await axe.run(document, {preload: false, runOnly: ['wcag2a','wcag2aa','wcag21aa','best-practice']});
                      return r.violations.map(v => v.id + ' x' + v.nodes.length + ': ' + v.nodes.slice(0,2).map(n => n.target.join(' ')).join(' | ')); }""")
                except Exception as e:
                    entry["errors"] = sorted(set(errs)) + ["load: " + str(e)[:200]]
                if "does-not-exist" in u:
                    entry["expect_404"] = entry.get("status") == 404
                    entry["errors"] = [e for e in entry.get("errors", []) if "404" not in e]
                if entry.get("errors") or entry.get("overflow") or entry.get("axe") or \
                        (entry.get("status") != 200 and "does-not-exist" not in u) or entry.get("expect_404") is False:
                    report["pages"].append(entry)
                pg.close()
            ctx.close()
        browser.close()

    report["summary"]["page_views_with_problems"] = len(report["pages"])
    report["summary"]["broken_internal"] = len(report["broken_internal"])
    report["summary"]["stale_assets"] = len(report["stale_assets"])
    print("LIVE-CHECK-BEGIN")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("LIVE-CHECK-END")


if __name__ == "__main__":
    main()
