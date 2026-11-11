import copy
import html
import json
import unittest
from unittest.mock import patch

import build_extras
import build_next_steps as ns


class NextStepTests(unittest.TestCase):
    def test_all_eighteen_sources_have_two_reviewed_links(self):
        data = ns.load()
        self.assertEqual(len(data["story"]), 10)
        self.assertEqual(len(data["exercise"]), 8)
        for kind, entries in data.items():
            for sid, entry in entries.items():
                self.assertEqual(len(entry["links"]), 2)
                self.assertEqual(entry["links"][0]["kind"], "concept")
                self.assertEqual(entry["links"][1]["kind"], "exercise" if kind == "story" else "story")
                rendered = ns.render(html.escape, kind, sid, entry)
                self.assertEqual(rendered.count('target="_blank" rel="noopener"'), 2)
                self.assertIn("مش تشخيص أو خطة علاج", rendered)
                self.assertIn("الروابط بتفتح في لسان جديد", rendered)

    def test_withdrawn_stories_are_hidden_in_both_directions(self):
        approved = build_extras.eligible_stories()
        withdrawn = next(x for x in approved if x["id"] == "anxiety-and-stress")
        with patch.object(build_extras, "eligible_stories",
                          return_value=[x for x in approved if x["id"] != withdrawn["id"]]):
            data = ns.load()
        self.assertNotIn(withdrawn["id"], data["story"])
        for sid in ("mindful-breathing", "fact-or-thought"):
            self.assertEqual(len(data["exercise"][sid]["links"]), 1)
            self.assertNotIn(withdrawn["title"], ns.render(
                html.escape, "exercise", sid, data["exercise"][sid]))

    def fixture(self):
        raw = {"stories": [{"id": "story-one", "concept": "term-one", "exercise": "exercise-one"}],
               "exercises": [{"id": "exercise-one", "concept": "term-one", "story": "story-one"}]}
        stories = {"story-one": (7, {"title": "Story"})}
        exercises = {"exercise-one": {"title": "Exercise"}}
        terms = {"term-one": {"title": "Term"}}
        return raw, stories, exercises, terms, {"story-one"}

    def test_story_anchor_uses_current_approved_order(self):
        data = ns.resolve(*self.fixture())
        self.assertEqual(data["exercise"]["exercise-one"]["links"][1]["href"], "/stories/#story-7")

    def test_invalid_reference_and_duplicate_fail_build(self):
        for mutation in ("concept", "exercise", "id", "duplicate"):
            fixture = list(copy.deepcopy(self.fixture()))
            record = fixture[0]["stories"][0]
            if mutation == "duplicate":
                fixture[0]["stories"].append(copy.deepcopy(record))
            else:
                record[mutation] = "unknown"
            with self.assertRaises(ValueError):
                ns.resolve(*fixture)

    def test_render_escapes_titles_and_notes(self):
        fixture = list(self.fixture())
        fixture[0]["stories"][0]["note"] = '<script>alert("note")</script>'
        fixture[2]["exercise-one"]["title"] = '<img src=x onerror="bad()">'
        data = ns.resolve(*fixture)
        text = ns.render(html.escape, "story", "story-one", data["story"]["story-one"])
        self.assertNotIn("<script>", text)
        self.assertNotIn("<img", text)
        self.assertIn("&lt;img", text)

    def test_no_entry_produces_no_empty_section(self):
        self.assertEqual(ns.render(html.escape, "story", None, None), "")

    def test_static_content_does_not_add_tracking_or_storage(self):
        for entry in ns.load()["story"].values():
            text = ns.render(html.escape, "story", "example", entry)
            for forbidden in ("<script", "<form", "<button", "localStorage", "onclick="):
                self.assertNotIn(forbidden, text)
        raw = json.loads((ns.ROOT / "content/next-steps.json").read_text())
        self.assertNotIn("href", json.dumps(raw))

    def test_exercise_enhancement_is_cache_versioned(self):
        self.assertRegex(build_extras._extras_script(), r'/assets/extras\.js\?v=[0-9a-f]{12}')
        self.assertRegex(build_extras._asset("exercise-fallback.css"), r'\?v=[0-9a-f]{12}$')

    def test_readonly_fallback_requires_successful_initialization(self):
        css = (ns.ROOT / "assets/exercise-fallback.css").read_text()
        script = (ns.ROOT / "assets/extras.js").read_text()
        self.assertIn(".extras:not(.exercise-enhanced) .ex[hidden] { display:block !important; }", css)
        self.assertIn(".extras:not(.exercise-enhanced) .journal", css)
        self.assertIn("ex.classList.add('exercise-enhanced')", script)


if __name__ == "__main__":
    unittest.main()
