"""Offline regression tests; the full site/browser checks run in Actions."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import home_clarity as hc

HEADER = '<header class="topbar"><nav><a href="/articles/">Articles</a></nav></header>'
FOOTER = '<footer><a href="/privacy/">Privacy</a></footer><script src="/assets/nav.js"></script>'
HOME = ('<!doctype html><html lang="ar"><head><meta charset="utf-8"><title>Home</title></head><body>'
        + HEADER + '<main id="main"><section class="hero hero-dark"><h1>Old</h1></section>'
        '<section class="section concern-finder"><h2 id="concern-title">Needs</h2></section>'
        '<section class="section discovery-hub">Duplicate</section>'
        '<!-- GROWTH-GUIDE:BEGIN --><details><summary>Guide</summary><section class="section guide">Guide</section></details><!-- GROWTH-GUIDE:END -->'
        '<section class="quick-quiz section">Quiz</section><section class="section myth-promo">Myth</section>'
        '<section class="tests-band">Tests</section><section class="quote-band">Quote</section>'
        '<section id="articles">Articles</section><section id="about">About</section>'
        '<section id="credentials">Credentials</section><!-- RESEARCH-LINK --><a href="/research/">Research</a>'
        '</main>' + FOOTER + '</body></html>')


class HomepageTests(unittest.TestCase):
    def test_reviewed_sections_removed(self):
        output = hc.transform(HOME)
        for name in hc.REMOVED:
            self.assertNotIn('class="' + name, output)
            self.assertNotIn('section ' + name, output)
        self.assertNotIn('GROWTH-GUIDE', output)

    def test_header_and_footer_unchanged(self):
        output = hc.transform(HOME)
        self.assertIn(HEADER, output)
        self.assertIn(FOOTER, output)

    def test_retains_content(self):
        output = hc.transform(HOME)
        for marker in ('id="articles"', 'id="about"', 'id="credentials"', 'id="concern-title"'):
            self.assertIn(marker, output)

    def test_research_link_moves_to_menu(self):
        # 2026-11-10: the observatory is in the menu, not a homepage link.
        link = '<!-- RESEARCH-LINK --><div class="wrap"><p><a href="/research/">مرصد الأبحاث النفسية: عرض علمي وشرح مبسط</a></p></div>'
        output = hc.transform(HOME.replace('<!-- RESEARCH-LINK --><a href="/research/">Research</a>', link))
        self.assertIn('<!-- RESEARCH-LINK -->', output)
        self.assertNotIn('مرصد الأبحاث النفسية: عرض علمي', output)
        self.assertEqual(hc.transform(output), output)

    def test_repeatable_and_single_heading_stylesheet(self):
        output = hc.transform(HOME)
        self.assertEqual(hc.transform(output), output)
        self.assertEqual(output.count('<h1'), 1)
        self.assertEqual(output.count('href="/assets/home-clarity.css"'), 1)

    def test_does_not_match_class_prefixes(self):
        extra = '<section class="section guide-extra">Keep</section><section class="discovery-hub-extra">Keep too</section>'
        self.assertIn(extra, hc.transform(HOME.replace('</main>', extra + '</main>')))

    def test_glossary_section_moves_to_menu(self):
        # 2026-11-10: the glossary is in the menu, not a homepage section.
        output = hc.transform(HOME.replace("</main>", hc.GLOSSARY + "</main>"))
        self.assertEqual(output.count('id="glossary-home-title"'), 0)
        self.assertNotIn("افتح القاموس النفسي", output)
        self.assertEqual(hc.transform(output), output)

    def test_nested_removed_section_rejected(self):
        broken = HOME.replace('Duplicate</section>', '<section>Nested</section></section>')
        with self.assertRaises(ValueError):
            hc.transform(broken)

    def test_duplicate_hero_rejected(self):
        with self.assertRaises(ValueError):
            hc.transform(HOME.replace('</main>', '<section class="hero">Other</section></main>'))

    def test_missing_structure_rejected(self):
        for old, new in (('id="concern-title"', 'id="changed"'), ('</head>', ''), ('</main>', '')):
            with self.subTest(old=old), self.assertRaises(ValueError):
                hc.transform(HOME.replace(old, new))

    def test_only_home_written_and_second_apply_noop(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'index.html').write_text(HOME, encoding='utf-8')
            (root / 'other.html').write_text('Untouched', encoding='utf-8')
            self.assertTrue(hc.apply(root))
            with patch.object(Path, 'write_text', side_effect=AssertionError('Unexpected write')):
                self.assertFalse(hc.apply(root))
            self.assertEqual((root / 'other.html').read_text(), 'Untouched')

    def test_invalid_input_not_written(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'index.html'
            path.write_text('Unexpected template', encoding='utf-8')
            with self.assertRaises(ValueError):
                hc.apply(Path(d))
            self.assertEqual(path.read_text(), 'Unexpected template')


    def test_shared_finalizer_reapplies_design_after_growth(self):
        import add_analytics
        import json
        import re
        import types
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / 'index.html'
            path.write_text(HOME, encoding='utf-8')
            def growth(_):
                text = path.read_text(encoding='utf-8')
                path.write_text(text.replace('</main>', '<section class="quick-quiz">Regenerated</section></main>'), encoding='utf-8')
            modules = {
                'site_header': types.SimpleNamespace(sync=lambda: None),
                'sitemap_policy': types.SimpleNamespace(apply=lambda _: False),
                'growth_package': types.SimpleNamespace(apply_pages=growth),
            }
            with patch.object(add_analytics, 'ROOT', str(root)), patch.dict('sys.modules', modules):
                add_analytics.main()
                first = path.read_text(encoding='utf-8')
                add_analytics.main()
                self.assertEqual(path.read_text(encoding='utf-8'), first)
            self.assertIn('clarity-hero', first)
            self.assertNotIn('quick-quiz', first)
            self.assertIn(HEADER, first)
            self.assertEqual(first.count('Content-Security-Policy'), 1)
            self.assertEqual(first.count('<!-- Cloudflare Web Analytics -->'), 1)
            beacon = re.search(r"data-cf-beacon='([^']+)'", first).group(1)
            self.assertEqual(json.loads(beacon), {'token': add_analytics.TOKEN})


if __name__ == '__main__':
    unittest.main()
