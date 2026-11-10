"""Curated path references, privacy boundaries, rendering and homepage entry."""
import copy
import html
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch

import build_your_path as yp
import home_clarity


class PathTests(unittest.TestCase):
    def test_six_topics_resolve_to_three_existing_public_resources(self):
        topics = yp.load()
        self.assertEqual(len(topics), 6)
        self.assertEqual(len({t["id"] for t in topics}), 6)
        for topic in topics:
            self.assertEqual([r["kind"] for r in topic["resources"]], list(yp.KINDS))
            for resource in topic["resources"]:
                path, _, fragment = resource["href"].partition("#")
                target = yp.ROOT / path.strip("/") / "index.html"
                self.assertTrue(target.is_file(), target)
                if fragment:
                    self.assertIn(f'id="{fragment}"', target.read_text(encoding="utf-8"))

    def test_native_links_available_without_scripts_and_no_personal_input(self):
        output = yp.body_html(yp.load())
        self.assertEqual(output.count('class="yp-route"'), 6)
        self.assertEqual(output.count('class="yp-step"'), 18)
        self.assertEqual(output.count('target="_blank" rel="noopener"'), 18)
        self.assertEqual(output.count("data-complete hidden"), 18)
        self.assertNotIn("<input", output)
        self.assertNotIn("<textarea", output)
        self.assertNotIn("<form", output)
        self.assertNotIn("بحسب تأكيده", output)
        self.assertIn("مش بتتبعت أو بتتحفظ", output)
        script = (yp.ROOT / "assets/your-path.js").read_text(encoding="utf-8")
        for pattern in (r"\blocalStorage\b", r"\bsessionStorage\b", r"\bfetch\s*\(",
                        r"\bXMLHttpRequest\b", r"\bsendBeacon\s*\(", r"\.cookie\b"):
            self.assertIsNone(re.search(pattern, script), pattern)

    def test_html_escaping(self):
        topics = copy.deepcopy(yp.load()[:1])
        topics[0]["label"] = '<script>alert("x")</script>'
        topics[0]["resources"][0]["title"] = "<img src=x>"
        output = yp.body_html(topics)
        self.assertIn(html.escape(topics[0]["label"]), output)
        self.assertNotIn("<script>", output)
        self.assertNotIn("<img", output)

    def test_missing_resource_and_duplicate_topic_rejected(self):
        original_read = Path.read_text
        topics = json.loads((yp.ROOT / "content/your-path.json").read_text(encoding="utf-8"))
        bad = copy.deepcopy(topics)
        bad["topics"][0]["story"] = "not-an-approved-story"
        duplicate = copy.deepcopy(topics)
        duplicate["topics"].append(copy.deepcopy(duplicate["topics"][0]))
        for data in (bad, duplicate):
            def read(path, *args, **kwargs):
                return json.dumps(data) if path == yp.ROOT / "content/your-path.json" else original_read(path, *args, **kwargs)
            with patch.object(Path, "read_text", read):
                with self.assertRaises(ValueError):
                    yp.load()

    def test_home_section_routes_each_concern_and_preserves_discovery(self):
        section = yp.home_section()
        self.assertEqual(section.count('class="concern-card"'), 6)
        for topic in yp.load():
            self.assertIn(f'href="/your-path/#{topic["id"]}"', section)
        self.assertIn('href="/discover-feelings/"', home_clarity.HERO)


if __name__ == "__main__":
    unittest.main()
