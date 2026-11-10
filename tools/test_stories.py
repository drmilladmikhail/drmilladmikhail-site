"""Disclosure, consent and rendering safeguards for the recovery-story cards."""
import html
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import build_extras


class StoryTests(unittest.TestCase):
    def render(self, records, reflections=None):
        captured = {}
        ba = SimpleNamespace(esc=html.escape, discussion_block=lambda *args: "")
        def page(*args):
            return "<html><head></head><body>" + args[3] + "</body></html>"
        def load(name, default):
            return {"stories": records} if name == "stories.json" else {"items": reflections or []}
        with patch.object(build_extras, "_load", side_effect=load):
            build_extras.stories_page(ba, page, lambda slug, value: captured.update(html=value), "https://example.com")
        return captured["html"]

    def test_ten_first_person_clinical_accounts_with_owner_confirmed_consent(self):
        data = json.loads((Path(build_extras.ROOT) / "content/stories.json").read_text(encoding="utf-8"))
        records = data["stories"]
        self.assertEqual(len(records), 10)
        self.assertEqual(len({s["id"] for s in records}), 10)
        for story in records:
            self.assertEqual(story["kind"], "clinician_provided_account")
            self.assertIs(story["owner_approved"], True)
            self.assertIs(story["deidentified"], True)
            self.assertIs(story["patient_publication_consent"], True)
            self.assertEqual(story["narrative_voice"], "editorial_first_person")
            self.assertEqual(len(story["text"]), 3)
            self.assertFalse({"source", "alias", "consent"} & story.keys())
        rendered = self.render(records)
        self.assertEqual(rendered.count('class="story-details"'), 10)
        self.assertEqual(rendered.count("صياغة تحريرية على لسان صاحب الحكاية، وليست اقتباسًا حرفيًا."), 10)
        self.assertIn("الحكايات دي من واقع عيادتي، وبنشرها بموافقة أصحابها", rendered)
        self.assertIn("مش نقل حرفي لكلامه", rendered)
        self.assertNotIn("بحسب تأكيده", rendered)
        self.assertNotIn("روايات قدّمها د. ميلاد", rendered)
        self.assertNotIn('class="story-source"', rendered)
        self.assertNotIn('class="story-cite"', rendered)
        self.assertNotIn("نُشرت بإذنه", rendered)
        self.assertNotIn('href="https://', rendered)

    def test_reader_consent_must_be_explicit_true_and_unknown_kind_is_not_published(self):
        base = {"title": "قارئ", "tag": "", "text": ["فقرة"], "alias": "اسم مستعار"}
        rendered = self.render([
            dict(base, title="مرفوض بدون موافقة"),
            dict(base, title="مرفوض موافقة نصية", consent="true"),
            dict(base, title="مرفوض نوع غير معروف", kind="unknown", consent=True),
            dict(base, title="قارئ موافق", consent=True),
        ])
        self.assertIn("قارئ موافق", rendered)
        self.assertNotIn("مرفوض", rendered)
        self.assertIn("نُشرت بإذنه", rendered)
        self.assertEqual(rendered.count('class="story-details"'), 1)

    def test_clinical_records_need_owner_approval_deidentification_and_confirmed_consent(self):
        base = {"kind": "clinician_provided_account", "title": "غير جاهزة", "text": ["فقرة"]}
        for flags in [{}, {"owner_approved": True}, {"deidentified": True},
                      {"owner_approved": True, "deidentified": True}]:
            self.assertNotIn('class="story-details"', self.render([dict(base, **flags)]))

    def test_story_text_is_escaped(self):
        rendered = self.render([{
            "kind": "illustrative_fiction", "title": "<script>bad()</script>",
            "text": ['<img src=x onerror="bad()">'], "tag": "توضيح",
        }])
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<img src=x", rendered)
        self.assertNotIn("<script>bad()", rendered)

    def test_every_story_has_three_hypothetical_choices_without_scripts_or_forms(self):
        records = json.loads((Path(build_extras.ROOT) / "content/stories.json").read_text())["stories"]
        prompts = list(build_extras.story_reflections().values())
        self.assertEqual({s["id"] for s in records}, {p["story_id"] for p in prompts})
        self.assertEqual(len(prompts), 10)
        rendered = self.render(records, prompts)
        self.assertEqual(rendered.count('class="story-reflection"'), 10)
        self.assertEqual(rendered.count('class="reflection-option"'), 30)
        self.assertEqual(rendered.count("موقف افتراضي للتفكير، مش تكملة لأحداث الحكاية."), 10)
        for prompt in prompts:
            fragment = build_extras.story_reflection_html(html.escape, prompt)
            self.assertEqual(fragment.count(f'name="reflection-{prompt["story_id"]}"'), 3)
            self.assertNotIn("<script", fragment)
            self.assertNotIn("<form", fragment)
            self.assertNotIn("onclick", fragment)
            self.assertNotIn("data-track", fragment)
        self.assertIn("مش بتتبعت أو بتتحفظ", rendered)

    def test_prompt_validation_and_escaping(self):
        good = {"story_id": "sample", "question": "Question", "options": [
            {"label": "Label", "text": "Text"} for _ in range(3)]}
        for items in ([good, good], [dict(good, story_id='bad" id')], [dict(good, options=[])],
                      [dict(good, question="")], [dict(good, options=[{}, {}, {}])]):
            with patch.object(build_extras, "_load", return_value={"items": items}):
                with self.assertRaises(ValueError):
                    build_extras.story_reflections()
        malicious = dict(good, question="<script>question()</script>", options=[
            {"label": "<img src=x>", "text": "<script>bad()</script>"} for _ in range(3)])
        fragment = build_extras.story_reflection_html(html.escape, malicious)
        self.assertIn("&lt;script&gt;", fragment)
        self.assertNotIn("<script>", fragment)
        self.assertNotIn("<img", fragment)


if __name__ == "__main__":
    unittest.main()
