import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from daily_research import process, eligible, validate_generated, FIELDS

TODAY = date(2026, 11, 8)
SOURCE = {'source': 'MED', 'id': '999', 'doi': '10.1234/synthetic-test', 'title': 'Synthetic research fixture', 'firstPublicationDate': '2026-11-01', 'abstractText': 'Synthetic abstract with 100 participants.', 'pubTypeList': {'pubType': ['Journal Article']}}

class DailyResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'content').mkdir()
        (self.root / 'content/research-body.html').write_text('<main></main>')

    def fetch_source(self, *args):
        return {'resultList': {'result': [dict(SOURCE)]}}

    def test_unconfigured_collects_metadata_without_paid_call(self):
        calls = []
        def fetch(*args):
            calls.append(args)
            return self.fetch_source()
        row = process(self.root, TODAY, fetch=fetch)
        self.assertEqual(row['status'], 'source_only')
        self.assertEqual(len(calls), 1)
        self.assertNotIn('abstractText', row)
        self.assertNotIn('academic_ar', row)

    def test_same_day_does_not_repeat(self):
        process(self.root, TODAY, fetch=self.fetch_source)
        def forbidden(*args):
            raise AssertionError('Unexpected network call')
        self.assertIsNone(process(self.root, TODAY, fetch=forbidden))

    def test_retracted_and_future_sources_rejected(self):
        self.assertFalse(eligible(dict(SOURCE, isRetracted='Y'), TODAY, set(), set()))
        self.assertFalse(eligible(dict(SOURCE, firstPublicationDate='2026-12-01'), TODAY, set(), set()))

    def test_duplicate_doi_rejected_case_insensitively(self):
        self.assertFalse(eligible(SOURCE, TODAY, set(), {SOURCE['doi'].upper().casefold()}))

    def test_generated_fields_require_arabic_and_grounded_numbers(self):
        generated = {k: ('عرض عربي تجريبي' if k.endswith('_ar') else 'Synthetic editorial brief') for k in FIELDS}
        self.assertEqual(validate_generated(generated, SOURCE['abstractText']), generated)
        generated['academic_ar'] = 'نتيجة غير موثقة 9999'
        with self.assertRaises(ValueError):
            validate_generated(generated, SOURCE['abstractText'])

    def test_paid_path_prepares_draft_not_publication(self):
        generated = {k: ('عرض عربي تجريبي' if k.endswith('_ar') else 'Synthetic editorial brief') for k in FIELDS}
        def fetch(url, *args):
            if 'europepmc' in url:
                return self.fetch_source()
            return {'choices': [{'message': {'content': json.dumps(generated)}}]}
        row = process(self.root, TODAY, key='synthetic-test-key', model='synthetic-test-model', fetch=fetch)
        self.assertEqual(row['status'], 'draft')
        self.assertEqual(row['basis'], 'abstract_only')
        self.assertFalse((self.root / 'research').exists())

if __name__ == '__main__':
    unittest.main()
