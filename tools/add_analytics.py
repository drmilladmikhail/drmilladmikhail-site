#!/usr/bin/env python3
"""Add the Cloudflare Web Analytics snippet to every HTML page of the site.

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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = "49dc5ec3f58f4825b6e04626f92dd475"
SNIPPET = ("<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
           "data-cf-beacon='{\"token\": \"" + TOKEN + "\"}'></script><!-- End Cloudflare Web Analytics -->")
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
            if TOKEN in t or "</body>" not in t:
                continue
            i = t.rfind("</body>")
            t = t[:i] + SNIPPET + "\n" + t[i:]
            with open(path, "w", encoding="utf-8") as f:
                f.write(t)
            changed.append(os.path.relpath(path, ROOT))
    print(f"analytics: added to {len(changed)} page(s)" + (": " + ", ".join(changed) if changed else ""))


if __name__ == "__main__":
    main()
