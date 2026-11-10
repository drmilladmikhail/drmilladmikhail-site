import html
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import build_explore as be
import build_extras
import build_glossary
import build_articles
from urllib.parse import unquote


class ExploreTests(unittest.TestCase):
    def test_indexes_all_public_sources_and_interleaves_types(self):
        data = be.records()
        expected = len(build_extras.eligible_stories()) + len(
            build_extras._load("exercises.json", {})["items"]) + len(build_glossary.load(be.ROOT)["items"]) + len(
                build_articles.load()) + len(build_extras._load("research-library.json", []))
        self.assertEqual(len(data), expected)
        self.assertEqual(len({r["id"] for r in data}), expected)
        self.assertEqual([r["kind"] for r in data[:3]], ["story", "exercise", "concept"])
        self.assertEqual([r["kind"] for r in data[:5]], list(be.LABELS))

    def test_articles_use_reviewed_titles_descriptions_and_exact_links(self):
        actual = {r["id"]: r for r in be.records()}
        for article in build_articles.load():
            row = actual["article:" + article["slug"]]
            self.assertEqual(row["title"], article["title"])
            self.assertEqual(row["summary"], article["description"])
            self.assertEqual(row["href"], "/articles/" + article["slug"] + "/")

    def test_research_metadata_and_links_work_with_and_without_pmid(self):
        actual = {r["id"]: r for r in be.records()}
        for paper in build_extras._load("research-library.json", []):
            row = actual["research:" + paper["doi"]]
            self.assertEqual(row["title"], paper["title_ar"])
            self.assertEqual(row["secondary"], paper["title"])
            self.assertIn(paper["doi"], row["search"])
            for author in paper["authors"]:
                self.assertIn(author, row["search"])
            self.assertEqual(unquote(row["href"].split("#")[1]),
                             "p" + str(paper.get("pmid") or paper["doi"]))

    def test_withdrawn_story_does_not_enter_index(self):
        approved = build_extras.eligible_stories()
        with patch.object(build_extras, "eligible_stories", return_value=approved[1:]):
            data = be.records()
        self.assertNotIn("story:" + approved[0]["id"], {r["id"] for r in data})
        new_first = next(r for r in data if r["kind"] == "story")
        self.assertEqual(new_first["href"], "/stories/#story-1")

    def test_never_indexes_clinical_narrative_paragraphs(self):
        serialized = json.dumps(be.records(), ensure_ascii=False)
        for item in build_extras.eligible_stories():
            for paragraph in item["text"]:
                self.assertNotIn(paragraph, serialized)

    def test_includes_english_aliases_and_reviewed_topic_synonyms(self):
        data = {r["id"]: r for r in be.records()}
        self.assertIn("Self-compassion", data["concept:self-compassion"]["search"])
        self.assertIn("وفاة", data["story:loss-of-parents"]["search"])
        self.assertIn("تدوين", data["exercise:feelings-journal"]["search"])

    def test_all_links_are_internal_and_of_the_expected_type(self):
        patterns = {"story": r"^/stories/#story-\d+$", "exercise": r"^/exercise/#[a-z0-9-]+$",
                    "concept": r"^/glossary/[a-z0-9-]+/$",
                    "article": r"^/articles/[a-z0-9-]+/$",
                    "research": r"^/research/library/#p[0-9A-Za-z.%-]+$"}
        for r in be.records():
            self.assertRegex(r["href"], patterns[r["kind"]])

    def test_html_is_safe_and_progressively_enhanced(self):
        output = {}
        ba = SimpleNamespace(esc=html.escape)
        def page(*args):
            return "<html><head></head><body>" + args[3] + "</body></html>"
        with patch.object(be, "records", return_value=[{
                "id": "story:example", "kind": "story", "title": '<script>alert("x")</script>',
                "summary": "<img src=x>", "search": 'foo" onclick="bad()', "href": "/stories/#story-1"}]):
            be.build(ba, page, lambda slug, value: output.update(html=value), "https://example.com")
        text = output["html"]
        self.assertNotIn('<script>alert(', text)
        self.assertNotIn("<img src=x>", text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn('class="explore-controls" hidden', text)
        self.assertIn('target="_blank" rel="noopener"', text)
        self.assertNotIn('name="q"', text)

    def test_search_has_no_storage_network_or_url_serialization(self):
        script = (be.ROOT / "assets/explore.js").read_text()
        for forbidden in ("localStorage", "sessionStorage", "fetch(", "sendBeacon(",
                          "XMLHttpRequest", "URLSearchParams", "innerHTML", "eval("):
            self.assertNotIn(forbidden, script)
        self.assertIn("event.preventDefault()", script)
        self.assertIn("window.addEventListener('pagehide', reset)", script)


if __name__ == "__main__":
    unittest.main()
