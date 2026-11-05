#!/usr/bin/env python3
"""Add the Cloudflare Web Analytics snippet and the security meta tags to every HTML page.

Security (the site is hosted on GitHub Pages, which can't send custom HTTP headers):
a Content-Security-Policy meta tag lists exactly which outside services a page may
load from (Google Fonts, Unsplash and YouTube images, the YouTube player, Cloudflare
analytics) and forbids inline scripts, plus a Referrer-Policy meta tag. If you add a
new outside service (e.g. an AI chat API), add its host to CSP below and run this.

Cloudflare Web Analytics counts visits and page views without cookies and
without tracking individual visitors, so no cookie banner is needed.
Dashboard: dash.cloudflare.com → Web Analytics → drmilladmikhail.com

Run:  python3 tools/add_analytics.py
The build scripts (build_articles.py, build_tests.py, build_videos.py) call it
at the end, and the GitHub Action .github/workflows/site-checks.yml runs it
after every push, so any new page gets the snippet automatically.
It only touches full pages (with </body>) that don't have the snippet yet.
"""
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
       "object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests")
SECURITY = (f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
            '<meta name="referrer" content="strict-origin-when-cross-origin">\n')
SKIP_DIRS = {".git", ".github", "tools", "node_modules", "content"}


def main():
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
    print(f"analytics/security: updated {len(changed)} page(s)" + (": " + ", ".join(changed) if changed else ""))


if __name__ == "__main__":
    main()
