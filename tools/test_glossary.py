"""Offline content, accessibility and generation regression checks."""
import json
from pathlib import Path
import tempfile
import unittest

import build_glossary as glossary


class GlossaryTests(unittest.TestCase):
    def setUp(self):
        self.data = glossary.load()

    def test_first_edition_has_eight_sourced_terms(self):
        self.assertEqual(len(self.data["items"]), 8)
        for term in self.data["items"]:
            self.assertTrue(term["source"]["url"].startswith("https://"))
            self.assertTrue(term["related"])
            self.assertIn("تخيّل", term["example"])

    def test_pages_are_static_linked_and_cited(self):
        index = glossary.index_page(self.data)
        self.assertEqual(index.count("<h1"), 1)
        self.assertIn('role="status"', index)
        self.assertIn('class="g-controls" hidden', index)
        self.assertIn('<dialog id="glossary-preview"', index)
        self.assertEqual(index.count('<template id="g-preview-'), 8)
        for tone in range(4):
            self.assertIn("g-tone-" + str(tone), index)
        self.assertNotIn("localStorage", index)
        for term in self.data["items"]:
            self.assertIn('/glossary/' + term["slug"] + '/', index)
            page = glossary.term_page(term, self.data)
            self.assertEqual(page.count("<h1"), 1)
            self.assertIn(term["source"]["url"], page)
            self.assertIn('rel="canonical"', page)
            self.assertIn("إيه اللي مش معناه؟", page)
            self.assertIn("مثال من يومك", page)
            self.assertIn("مش تشخيص", page)
            self.assertIn('href="/help-now/"', page)
            self.assertNotIn("reviewedBy", page)
            for block in page.split('<script type="application/ld+json">')[1:]:
                json.loads(block.split("</script>")[0])

    def test_generation_is_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "content").mkdir()
            (root / "content/glossary.json").write_text(json.dumps(self.data), encoding="utf-8")
            paths = glossary.build(root)
            first = [(root / path / "index.html").read_bytes() for path in paths]
            self.assertEqual(len(paths), 9)
            self.assertEqual(paths, glossary.build(root))
            self.assertEqual(first, [(root / path / "index.html").read_bytes() for path in paths])

    def test_invalid_relationship_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "content").mkdir()
            self.data["items"][0]["related"] = ["missing-term"]
            (root / "content/glossary.json").write_text(json.dumps(self.data), encoding="utf-8")
            with self.assertRaises(ValueError):
                glossary.load(root)


if __name__ == "__main__":
    unittest.main()
