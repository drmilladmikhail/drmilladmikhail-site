import html
import json
import unittest
from unittest.mock import patch

import build_extras
import build_saved


class SavedTests(unittest.TestCase):
    def test_catalog_has_all_ten_stories_and_eight_exercises(self):
        data = build_saved.catalog()
        self.assertEqual(sum(x["kind"] == "story" for x in data.values()), 10)
        self.assertEqual(sum(x["kind"] == "exercise" for x in data.values()), 8)
        self.assertTrue(all(set(x) == {"title", "kind", "url"} for x in data.values()))

    def test_each_consent_flag_is_required_in_catalog(self):
        item = {"id": "example", "title": "عنوان", "kind": "clinician_provided_account",
                "owner_approved": True, "deidentified": True, "patient_publication_consent": True}
        for field in ("owner_approved", "deidentified", "patient_publication_consent"):
            bad = dict(item, **{field: False})
            with patch.object(build_extras, "_load", side_effect=lambda name, default:
                              {"stories": [bad]} if name == "stories.json" else {"items": []}):
                self.assertEqual(build_saved.catalog(), {})

    def test_unknown_or_unconsented_reader_not_in_catalog(self):
        records = [{"id": "one", "title": "one", "kind": "unknown"},
                   {"id": "two", "title": "two", "consent": False}]
        with patch.object(build_extras, "_load", side_effect=lambda name, default:
                          {"stories": records} if name == "stories.json" else {"items": []}):
            self.assertEqual(build_saved.catalog(), {})

    def test_button_is_explicit_and_escapes_title(self):
        text = build_saved.button(html.escape, "story", "some-story", 'title" <script>')
        self.assertIn('type="button"', text)
        self.assertIn('aria-pressed="false" hidden', text)
        self.assertIn("احفظ على جهازي", text)
        self.assertNotIn("<script>", text)
        self.assertIn("&quot;", text)

    def test_invalid_ids_never_produce_buttons(self):
        for slug in (None, "", "../unsafe", '"><script>', "one:two"):
            self.assertEqual(build_saved.button(html.escape, "story", slug, "Title"), "")
        self.assertEqual(build_saved.button(html.escape, "answer", "one", "Title"), "")

    def test_script_never_accesses_other_storage_or_sends_answers(self):
        script = (build_saved.ROOT / "assets/bookmarks.js").read_text()
        self.assertNotIn("localStorage.clear", script)
        self.assertNotIn("journal:", script)
        self.assertNotIn("dm-challenges", script)
        for api in ("fetch(", "sendBeacon(", "XMLHttpRequest", "innerHTML"):
            self.assertNotIn(api, script)
        self.assertIn("localStorage.removeItem(KEY)", script)
        self.assertIn("JSON.stringify({ version: 1, items: next })", script)

    def test_generated_catalog_matches_approved_current_source(self):
        text = (build_saved.ROOT / "assets/bookmarks-catalog.js").read_text()
        saved = json.loads(text.split("window.DMBookmarkCatalog=", 1)[1].strip().rstrip(";"))
        self.assertEqual(saved, build_saved.catalog())


if __name__ == "__main__":
    unittest.main()
