"""The review gate: new articles can't be published without a summary, 2 sources, a category and a human review date."""
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_articles as ba  # noqa: E402

BASE = {"slug": "couples-counseling", "title": "t", "description": "d", "date": "2026-12-01",
        "category": "relationships-family", "summary": "s",
        "refs": [{"title": "a", "url": "https://a"}, {"title": "b", "url": "https://b"}], "reviewed_on": "2026-11-30"}


def run_load(entry):
    data = json.dumps([entry])
    with mock.patch("builtins.open", mock.mock_open(read_data=data)):
        return ba.load()


class Gate(unittest.TestCase):
    def test_reviewed_article_passes(self):
        self.assertEqual(run_load(dict(BASE))[0]["image"], "cat-relationships-family")

    def test_missing_review_blocks(self):
        for key in ("reviewed_on", "summary", "category"):
            e = dict(BASE)
            e.pop(key)
            with self.assertRaises(SystemExit, msg=key):
                run_load(e)

    def test_one_source_blocks(self):
        e = dict(BASE, refs=BASE["refs"][:1])
        with self.assertRaises(SystemExit):
            run_load(e)

    def test_live_articles_valid(self):
        self.assertTrue(len(ba.load()) >= 15)


if __name__ == "__main__":
    unittest.main()
