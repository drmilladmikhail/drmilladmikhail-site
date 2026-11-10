"""Regression coverage for the audited safety, layout and storage repairs."""
import json
from pathlib import Path
import unittest

import build_research
import build_worksheets
import pages_trust

ROOT = Path(__file__).resolve().parents[1]


class SiteRepairsTests(unittest.TestCase):
    def test_egypt_official_contact_is_not_general_health_number(self):
        row = pages_trust.HELPLINES[0][1][0]
        self.assertEqual(row[1:3], ("16328", "16328"))
        for folder in ("assets", "tools", "content"):
            for path in (ROOT / folder).rglob("*"):
                if path.suffix not in (".js", ".html", ".json", ".py") or path.name == Path(__file__).name:
                    continue
                text = path.read_text(encoding="utf-8")
                for obsolete in ('tel:105"', '>105<', "مصر: 105", "الدعم النفسي 105"):
                    self.assertNotIn(obsolete, text, str(path))

    def test_research_uses_readable_theme_tokens(self):
        self.assertIn("background:var(--surface)", build_research.CSS)
        self.assertIn("color:var(--ink)", build_research.CSS)
        self.assertIn("#lib-count,#lib-intro-count{color:var(--eucalyptus)}", build_research.LIB_CSS)
        self.assertIn(".test-refs", (ROOT / "assets/site.css").read_text())
        self.assertIn("overflow-wrap: anywhere", (ROOT / "assets/site.css").read_text())

    def test_journey_is_in_authoritative_content_and_survives_build(self):
        records = json.loads((ROOT / "content/challenges.json").read_text())
        self.assertEqual(len(records), 8)
        self.assertEqual(len({item["id"] for item in records}), 8)
        journey = next(item for item in records if item["id"] == "seven-day-journey")
        self.assertEqual(len(journey["tasks"]), 7)
        source = (ROOT / "tools/build_pages.py").read_text()
        for marker in ("data-journey-bar", "data-journey-badge", "data-journey-reset",
                       "data-journey-share", "data-ch-storage-hint"):
            self.assertIn(marker, source)

    def test_worksheet_has_verified_contact_and_clickable_citation(self):
        worksheet = json.loads((ROOT / "content/worksheets.json").read_text())["items"][0]
        text = build_worksheets.worksheet_html(worksheet)
        self.assertIn("16328<sup>1</sup>", text)
        self.assertIn('href="https://www.100millionseha.eg/happiness"', text)
        self.assertNotIn("مصر: 105", text)

    def test_repaired_scripts_are_cache_versioned_and_do_not_clear_other_data(self):
        source = (ROOT / "tools/add_analytics.py").read_text()
        for name in ("extras.js", "challenges.js", "my-space.js", "helper.js", "partner-check.js", "relcheck.js"):
            self.assertIn('"' + name + '"', source)
            self.assertNotIn("localStorage.clear(", (ROOT / "assets" / name).read_text())
        self.assertIn('ctx.direction = "rtl"', (ROOT / "assets/challenges.js").read_text())


if __name__ == "__main__":
    unittest.main()
