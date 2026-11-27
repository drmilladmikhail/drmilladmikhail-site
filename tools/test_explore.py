import json
import re
import unittest
from pathlib import Path

import build_explore as be


class ExploreGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = be.write_outputs()
        cls.explore_dir = be.ROOT / "explore"

    def test_extracts_all_five_content_types_and_links(self):
        nodes = self.graph["nodes"]
        links = self.graph["links"]
        types = {n["type"] for n in nodes}
        self.assertEqual(types, {"article", "feeling", "glossary", "exercise", "audio"})
        self.assertGreater(len(nodes), 60)
        self.assertGreater(len(links), 80)

        ids = {n["id"] for n in nodes}
        self.assertEqual(len(ids), len(nodes))
        for link in links:
            self.assertIn(link["source"], ids)
            self.assertIn(link["target"], ids)
            self.assertNotEqual(link["source"], link["target"])

    def test_all_node_hrefs_are_valid_internal_routes(self):
        for n in self.graph["nodes"]:
            self.assertTrue(n["href"].startswith("/"), n)
            self.assertNotIn("javascript:", n["href"].lower())

    def test_strict_csp_no_inline_scripts_or_handlers(self):
        html_text = (self.explore_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn('http-equiv="Content-Security-Policy"', html_text)
        self.assertIn('dir="rtl"', html_text)
        self.assertIn('lang="ar"', html_text)

        scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>", html_text, flags=re.I | re.S)
        self.assertGreaterEqual(len(scripts), 1)
        for attrs, body in scripts:
            if 'type="application/ld+json"' in attrs:
                json.loads(body)
            else:
                self.assertIn('src="/explore/explore.js', attrs)
                self.assertEqual(body.strip(), "")

        self.assertIsNone(re.search(r"\bon[a-z]+\s*=", html_text, flags=re.I))

    def test_bundle_size_strictly_under_150kb(self):
        files = ["index.html", "explore.css", "explore.js", "reading-corner.svg", "graph-data.json"]
        total_bytes = sum((self.explore_dir / name).stat().st_size for name in files)
        self.assertLess(total_bytes, 150 * 1024, f"Bundle size {total_bytes}B exceeds 150KB")


if __name__ == "__main__":
    unittest.main()
