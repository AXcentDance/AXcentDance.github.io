import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import maintain_breadcrumbs as mb
import breadcrumb_validation as bv


def html_fixture(parent_url="https://axcentdance.com/blog", final_url=None, date_modified="2026-03-31"):
    final_url = final_url or "https://axcentdance.com/de/blog-posts/example"
    return f"""<!doctype html>
<html lang="de">
<head>
  <link rel="canonical" href="https://axcentdance.com/de/blog-posts/example">
  <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "BlogPosting",
      "headline": "Example",
      "dateModified": "{date_modified}"
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{
          "@type": "ListItem",
          "position": 1,
          "name": "Startseite",
          "item": "https://axcentdance.com/de/"
        }},
        {{
          "@type": "ListItem",
          "position": 2,
          "name": "Blog",
          "item": "{parent_url}"
        }},
        {{
          "@type": "ListItem",
          "position": 3,
          "name": "Example",
          "item": "{final_url}"
        }}
      ]
    }}
  ]
}}
  </script>
</head>
<body></body>
</html>
"""


def english_html_fixture(parent_url="https://axcentdance.com/blog", final_url="https://axcentdance.com/blog-posts/example"):
    return f"""<!doctype html>
<html lang="en">
<head>
  <link rel="canonical" href="https://axcentdance.com/blog-posts/example">
  <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://axcentdance.com/"
        }},
        {{
          "@type": "ListItem",
          "position": 2,
          "name": "Blog",
          "item": "{parent_url}"
        }},
        {{
          "@type": "ListItem",
          "position": 3,
          "name": "Example",
          "item": "{final_url}"
        }}
      ]
    }}
  ]
}}
  </script>
</head>
<body></body>
</html>
"""


class BreadcrumbMaintenanceTests(unittest.TestCase):
    def write_fixture(self, root, relative_path, content):
        path = Path(root) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_repairs_german_blog_parent_and_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_fixture(root, "de/blog-posts/example.html", html_fixture())

            plan = mb.build_fix_plan(root, path)

            self.assertTrue(plan.has_changes)
            self.assertIn('"item": "https://axcentdance.com/de/blog"', plan.updated)
            self.assertIn(f'"dateModified": "{mb.TODAY}"', plan.updated)
            self.assertEqual(mb.validate_breadcrumb_content(plan.updated, "de/blog-posts/example.html"), [])

    def test_repairs_final_breadcrumb_to_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.write_fixture(
                root,
                "de/blog-posts/example.html",
                html_fixture(parent_url="https://axcentdance.com/de/blog", final_url="https://axcentdance.com/de/blog-posts/old"),
            )

            plan = mb.build_fix_plan(root, path)

            self.assertIn('"item": "https://axcentdance.com/de/blog-posts/example"', plan.updated)
            labels = [change.label for change in plan.changes]
            self.assertIn("final breadcrumb URL", labels)

    def test_fix_does_not_modify_matching_urls_outside_json_ld(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = (
                '<link rel="alternate" href="https://axcentdance.com/de/blog-posts/old">\n'
                + html_fixture(
                    parent_url="https://axcentdance.com/de/blog",
                    final_url="https://axcentdance.com/de/blog-posts/old",
                )
            )
            path = self.write_fixture(root, "de/blog-posts/example.html", content)

            plan = mb.build_fix_plan(root, path)

            self.assertIn('<link rel="alternate" href="https://axcentdance.com/de/blog-posts/old">', plan.updated)
            self.assertIn('"item": "https://axcentdance.com/de/blog-posts/example"', plan.updated)

    def test_idempotent_when_already_correct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = html_fixture(parent_url="https://axcentdance.com/de/blog", date_modified=mb.TODAY)
            path = self.write_fixture(root, "de/blog-posts/example.html", content)

            plan = mb.build_fix_plan(root, path)

            self.assertFalse(plan.has_changes)
            self.assertEqual(plan.changes, [])

    def test_invalid_json_reports_error(self):
        content = """<html><head><link rel="canonical" href="https://axcentdance.com/de/blog-posts/example"><script type="application/ld+json">{bad</script></head></html>"""

        issues = mb.validate_breadcrumb_content(content, "de/blog-posts/example.html")

        self.assertTrue(any("Invalid JSON" in issue for issue in issues))

    def test_shared_validator_accepts_valid_german_blog_breadcrumb(self):
        content = html_fixture(parent_url="https://axcentdance.com/de/blog")

        self.assertEqual(bv.validate_breadcrumb_content(content, "de/blog-posts/example.html"), [])

    def test_shared_validator_rejects_german_parent_without_de(self):
        issues = bv.validate_breadcrumb_content(html_fixture(), "de/blog-posts/example.html")

        self.assertTrue(any("missing /de/" in issue for issue in issues))

    def test_shared_validator_rejects_english_breadcrumb_with_de(self):
        issues = bv.validate_breadcrumb_content(
            english_html_fixture(parent_url="https://axcentdance.com/de/blog"),
            "blog-posts/example.html",
        )

        self.assertTrue(any("contains /de/" in issue for issue in issues))

    def test_shared_validator_rejects_final_breadcrumb_mismatch(self):
        issues = bv.validate_breadcrumb_content(
            html_fixture(parent_url="https://axcentdance.com/de/blog", final_url="https://axcentdance.com/de/blog-posts/old"),
            "de/blog-posts/example.html",
        )

        self.assertTrue(any("does not match canonical" in issue for issue in issues))

    def test_shared_validator_rejects_missing_breadcrumb(self):
        content = """<html><head><script type="application/ld+json">{"@context":"https://schema.org","@graph":[]}</script></head></html>"""

        issues = bv.validate_breadcrumb_content(content, "de/blog-posts/example.html")

        self.assertTrue(any("Missing BreadcrumbList" in issue for issue in issues))

    def test_dirty_unrelated_file_does_not_block_target(self):
        original = mb.git_dirty_paths
        try:
            mb.git_dirty_paths = lambda root: {"README.md"}
            plan = mb.FilePlan(Path("/tmp/repo/de/blog-posts/example.html"), "a", "b", [])
            mb.refuse_dirty_targets(Path("/tmp/repo"), [plan], force=False)
        finally:
            mb.git_dirty_paths = original

    def test_dirty_target_refuses_without_force(self):
        original = mb.git_dirty_paths
        try:
            mb.git_dirty_paths = lambda root: {"de/blog-posts/example.html"}
            plan = mb.FilePlan(Path("/tmp/repo/de/blog-posts/example.html"), "a", "b", [])
            with self.assertRaises(mb.BreadcrumbError):
                mb.refuse_dirty_targets(Path("/tmp/repo"), [plan], force=False)
        finally:
            mb.git_dirty_paths = original

    def test_dirty_target_allows_with_force(self):
        original = mb.git_dirty_paths
        try:
            mb.git_dirty_paths = lambda root: {"de/blog-posts/example.html"}
            plan = mb.FilePlan(Path("/tmp/repo/de/blog-posts/example.html"), "a", "b", [])
            mb.refuse_dirty_targets(Path("/tmp/repo"), [plan], force=True)
        finally:
            mb.git_dirty_paths = original


if __name__ == "__main__":
    unittest.main()
