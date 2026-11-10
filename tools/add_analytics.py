#!/usr/bin/env python3
"""Finalize navigation, security, analytics, sitemap and reviewed homepage."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = "49dc5ec3f58f4825b6e04626f92dd475"
SNIPPET = ("<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
           "data-cf-beacon='{\"token\": \"" + TOKEN + "\"}'></script><!-- End Cloudflare Web Analytics -->")
CSP = ("default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; "
       "img-src 'self' data: https://images.unsplash.com https://i.ytimg.com; "
       "frame-src https://www.youtube-nocookie.com; connect-src 'self' https://cloudflareinsights.com; "
       "object-src 'none'; base-uri 'self'; form-action 'self' https://formsubmit.co; upgrade-insecure-requests")
try:
    import json as _json
    with open(os.path.join(ROOT, "content", "comments.json"), encoding="utf-8") as _f:
        _c = _json.load(_f)
    if _c.get("app_id"):
        _h = _c.get("host", "https://cusdis.com")
        CSP = (CSP.replace("script-src 'self' ", f"script-src 'self' {_h} ")
                  .replace("frame-src ", f"frame-src {_h} ")
                  .replace("connect-src 'self' ", f"connect-src 'self' {_h} "))
except (OSError, ValueError):
    pass
SECURITY = (f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
            '<meta name="referrer" content="strict-origin-when-cross-origin">\n')
SKIP_DIRS = {".git", ".github", "tools", "node_modules", "content", "docs"}


def version_assets(root):
    """Version shared styles and interactive scripts so fixes bypass stale caches."""
    import hashlib
    vers = {}
    names = ("site.css", "nav.js", "home-clarity.css", "home-redesign.css",
             "extras.js", "challenges.js", "my-space.js", "helper.js", "partner-check.js", "relcheck.js",
             "share.js", "quiz.js")
    for name in names:
        path = os.path.join(root, "assets", name)
        if os.path.isfile(path):
            with open(path, "rb") as f:
                vers[name] = hashlib.md5(f.read()).hexdigest()[:8]
    pat = re.compile(r'(/assets/)(' + "|".join(re.escape(name) for name in names) + r')(\?v=[0-9a-f]+)?(")')
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as f:
                t = f.read()
            new = pat.sub(lambda m: f"{m.group(1)}{m.group(2)}?v={vers[m.group(2)]}{m.group(4)}" if m.group(2) in vers else m.group(0), t)
            if new != t:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                n += 1
    print(f"asset versions: updated {n} page(s)")


def main():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import site_header
    site_header.sync()
    changed = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8") as f:
                t = f.read()
            if "</body>" not in t:
                continue
            old = t
            t = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>\n?<meta name="referrer"[^>]*>\n?', "", t)
            t = re.sub(r'(<meta charset="utf-8">\n?)', lambda m: m.group(1) + SECURITY, t, count=1, flags=re.I)
            if TOKEN not in t:
                i = t.rfind("</body>")
                t = t[:i] + SNIPPET + "\n" + t[i:]
            if t == old:
                continue
            with open(path, "w", encoding="utf-8") as f:
                f.write(t)
            changed.append(os.path.relpath(path, ROOT))
    print(f"analytics/security: updated {len(changed)} page(s)")
    import sitemap_policy
    print(f"sitemap policy: changed={sitemap_policy.apply(ROOT)}")
    import growth_package
    growth_package.apply_pages(ROOT)
    import home_clarity
    home_clarity.apply(ROOT)
    import breadcrumbs
    breadcrumbs.apply(ROOT)
    version_assets(ROOT)


if __name__ == "__main__":
    main()
