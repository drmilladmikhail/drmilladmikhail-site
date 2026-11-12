#!/usr/bin/env python3
"""Fetch URLs in a real browser and print status, final URL, title and interesting links (url-probe.yml)."""
import json
import re
import sys
from playwright.sync_api import sync_playwright

out = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
                        locale="en-US")
    for u in sys.argv[1:]:
        pg = ctx.new_page()
        try:
            r = pg.goto(u, wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(2500)
            html = pg.content()
            links = sorted(set(re.findall(r'href="([^"]*(?:/stores/|/e/B0|/author/|/-/e/)[^"]*)"', html)))[:15]
            out.append({"url": u, "status": r.status if r else None, "final": pg.url, "title": pg.title()[:150],
                        "author_links": links, "byline": re.findall(r'class="author[^"]*"[^>]*>.{0,300}', html)[:2]})
        except Exception as e:
            out.append({"url": u, "error": str(e)[:200]})
        pg.close()
    b.close()
print("PROBE-BEGIN")
print(json.dumps(out, ensure_ascii=False, indent=1))
print("PROBE-END")
