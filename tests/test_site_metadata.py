import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_site_metadata import build, normalized_site_url


class SiteMetadataTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ("index.html", "fuel/index.html", "purchase/index.html",
                     "vehicles/hyundai-sonata-nf/index.html",
                     "vehicles/placeholder/index.html"):
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('<!doctype html><html><head><title>test</title></head><body>test</body></html>',
                         encoding="utf-8")
        p = self.root / "data" / "vehicle-details.json"
        p.parent.mkdir(parents=True)
        p.write_text('[{"id":"hyundai-sonata-nf"}]', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def sitemap_locations(self):
        tree = ET.parse(self.root / "sitemap.xml")
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        return [x.text for x in tree.findall(".//" + ns + "loc")]

    def test_project_path_and_idempotency(self):
        url = "https://david12448.github.io/car-maintenance-guide/"
        build(self.root, url)
        build(self.root, url)
        page = (self.root / "vehicles/hyundai-sonata-nf/index.html").read_text(encoding="utf-8")
        self.assertIn(url + "vehicles/hyundai-sonata-nf/", page)
        self.assertEqual(page.count('rel="canonical"'), 1)
        self.assertEqual(self.sitemap_locations(),
                         [url, url + "vehicles/hyundai-sonata-nf/"])
        self.assertNotIn("placeholder", (self.root / "sitemap.xml").read_text())

    def test_domain_switch_changes_only_base(self):
        build(self.root, "https://auto.prince-in-wonderworld.com")
        self.assertEqual(self.sitemap_locations(),
                         ["https://auto.prince-in-wonderworld.com/",
                          "https://auto.prince-in-wonderworld.com/vehicles/hyundai-sonata-nf/"])
        self.assertIn("auto.prince-in-wonderworld.com/purchase/",
                      (self.root / "purchase/index.html").read_text(encoding="utf-8"))

    def test_invalid_url_rejected(self):
        for url in ("http://example.com", "https://example.com/?x=1",
                    "https://example.com/#a", "https://user:secret@example.com"):
            with self.assertRaises(ValueError):
                normalized_site_url(url)


if __name__ == "__main__":
    unittest.main()
