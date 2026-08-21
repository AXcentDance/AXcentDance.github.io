import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import generate_md_pages as g


PAGE_FIXTURE = """<!doctype html>
<html lang="en">
<head>
  <title>Test Page | AXcent Dance</title>
  <meta name="description" content="A test description.">
  <link rel="canonical" href="https://axcentdance.com/test-page">
  <link rel="alternate" hreflang="de" href="https://axcentdance.com/de/test-page">
  <link rel="alternate" hreflang="x-default" href="https://axcentdance.com/test-page">
  <style>body { color: red; }</style>
  <script>var hidden = true;</script>
</head>
<body>
  <header><nav><a href="index.html">Home</a></nav></header>
  <main id="main-content">
    <h1>Main Heading</h1>
    <p>Intro paragraph with an <a href="schedule.html">internal link</a>
       and an <a href="https://example.com/x">external link</a>.</p>
    <h2>Subsection</h2>
    <ul>
      <li>First item</li>
      <li>Second item with <a href="/registration">a link</a></li>
    </ul>
    <a href="/#trial-form" class="btn"><span>Book Now</span>
      <svg viewBox="0 0 24 24"><path d="M0 0"/></svg></a>
    <div aria-hidden="true">decorative</div>
    <script>ignore()</script>
  </main>
  <footer><p>Footer text</p></footer>
</body>
</html>"""

FIXTURE_PAGES = {
    "test-page.html": PAGE_FIXTURE,
    "index.html": "<html></html>",
    "schedule.html": "<html></html>",
    "registration.html": "<html></html>",
}


class RenderPageTest(unittest.TestCase):
    def setUp(self):
        self._saved = g.PAGES
        g.PAGES = FIXTURE_PAGES

    def tearDown(self):
        g.PAGES = self._saved

    def render(self):
        return g.render_page("test-page.html", PAGE_FIXTURE)

    def test_header_block(self):
        out = self.render()
        self.assertIn("# Test Page | AXcent Dance\n", out)
        self.assertIn("> A test description.\n", out)
        self.assertIn("- Canonical (HTML): https://axcentdance.com/test-page\n", out)
        self.assertIn("- Language: en\n", out)
        self.assertIn(
            "- Translation (de): https://axcentdance.com/de/test-page\n", out)
        self.assertIn(g.TWIN_MARKER, out)

    def test_headings_and_lists(self):
        out = self.render()
        self.assertIn("# Main Heading\n", out)
        self.assertIn("## Subsection\n", out)
        self.assertIn("- First item\n", out)

    def test_internal_links_become_absolute_clean_urls(self):
        out = self.render()
        self.assertIn("[internal link](https://axcentdance.com/schedule)", out)
        self.assertIn("[a link](https://axcentdance.com/registration)", out)
        self.assertNotIn("schedule.html", out)

    def test_external_links_kept_verbatim(self):
        out = self.render()
        self.assertIn("[external link](https://example.com/x)", out)

    def test_block_level_cta_link_keeps_href(self):
        out = self.render()
        self.assertIn("[Book Now](https://axcentdance.com/)", out)

    def test_scripts_styles_and_hidden_content_dropped(self):
        out = self.render()
        self.assertNotIn("ignore()", out)
        self.assertNotIn("color: red", out)
        self.assertNotIn("decorative", out)
        self.assertNotIn("var hidden", out)

    def test_only_main_content_rendered(self):
        out = self.render()
        self.assertNotIn("Footer text", out)
        body = out.split("---", 1)[1]
        self.assertNotIn("[Home]", body)

    def test_deterministic(self):
        self.assertEqual(self.render(), self.render())


class HelperTest(unittest.TestCase):
    def test_twin_path(self):
        self.assertEqual(g.twin_path("schedule.html"), "schedule.md")
        self.assertEqual(g.twin_path("de/blog/post.html"), "de/blog/post.md")

    def test_index_url_collapses(self):
        saved = g.PAGES
        g.PAGES = FIXTURE_PAGES
        try:
            self.assertEqual(
                g.clean_url("index.html", "test-page.html"),
                "https://axcentdance.com/")
        finally:
            g.PAGES = saved

    def test_dedupe_consecutive(self):
        self.assertEqual(g.dedupe(["a", "a", "b", "a"]), ["a", "b", "a"])

    def test_is_twin_file_requires_marker(self):
        with tempfile.NamedTemporaryFile(
                "w", suffix=".md", delete=False) as f:
            f.write("# Hand-written doc\n\nNo marker here.\n")
            hand = f.name
        with tempfile.NamedTemporaryFile(
                "w", suffix=".md", delete=False) as f:
            f.write(f"# Twin\n\n{g.TWIN_MARKER}\n")
            twin = f.name
        self.assertFalse(g.is_twin_file(hand))
        self.assertTrue(g.is_twin_file(twin))
        self.assertFalse(g.is_twin_file(hand + ".does-not-exist"))


if __name__ == "__main__":
    unittest.main()
