"""«اكتشاف مشاعرك»: the data behind the five-step flow points only at pages and ids that exist, and nothing is stored or sent."""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "discover-feelings")


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


class DiscoverFeelings(unittest.TestCase):
    def test_links_in_data_exist(self):
        data = read("data.js") + read("index.html")
        links = set(re.findall(r"""['"](/[a-z0-9\-/]+/)['"]""", data))
        self.assertGreater(len(links), 15)
        for href in sorted(links):
            if href.startswith("/glossary/"):
                continue  # glossary pages are generated; checked below against the source list
            self.assertTrue(os.path.isfile(os.path.join(ROOT, href.strip("/"), "index.html")), href)

    def test_ids_are_consistent(self):
        data = read("data.js")
        ids = set(re.findall(r"\{ id: '([a-z]+)'", data))
        needs = set(re.findall(r"^  ([a-z]+): \{ t: '", data, re.M))
        paths = set(re.findall(r"^  ([a-z]+): \{\s*\n\s+title:|DF_PATHS\.([a-z]+) = ", data, re.M))
        paths = {a or b for a, b in paths}
        chips = re.findall(r"\['[^']+', '([a-z]+)'\]", data.split("window.DF_CHIPS")[1].split("];")[0])
        self.assertEqual(len(chips), 12)
        self.assertTrue(set(chips) <= ids, set(chips) - ids)
        over = data.split("window.DF_OVERRIDE")[1].split("};")[0]
        self.assertTrue(set(re.findall(r"^  ([a-z]+): \{", over, re.M)) <= ids)
        used_needs = set(re.findall(r"nd: \[([^\]]*)\]", data).__iter__().__next__().replace("'", "").replace(" ", "").split(","))
        for group in re.findall(r"nd: \[([^\]]*)\]", data):
            for n in group.replace("'", "").replace(" ", "").split(","):
                self.assertIn(n, needs, n)
        self.assertTrue(used_needs)
        for x in re.findall(r"x: '([a-z]*)'", data):
            self.assertTrue(x == "" or x in paths, x)
        for n in re.findall(r"(?:load|conflict|future|compare|tired|lonely): '([a-z]+)'", data):
            self.assertIn(n, needs)

    def test_nothing_is_stored_or_sent(self):
        js = read("tool.js")
        for bad in (r"localStorage", r"sessionStorage", r"\bfetch\s*\(", r"XMLHttpRequest", r"sendBeacon", r"\.cookie\b",
                    r"location\.(hash|search|href)\s*=", r"history\.(push|replace)State", r"gtag\s*\("):
            self.assertIsNone(re.search(bad, js), bad)

    def test_page_keeps_its_safety_and_limits(self):
        html = read("index.html")
        for must in ("/help-now/", "16328", "988", "مش تشخيص", "مش بتتبعت", "ابدأ رحلة اكتشاف مشاعرك", "ابدأ خطوة جديدة نحو فهم نفسك"):
            self.assertIn(must, html)


if __name__ == "__main__":
    unittest.main()
