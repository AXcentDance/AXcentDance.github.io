import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "topic_map.py"
SPEC = importlib.util.spec_from_file_location("topic_map", MODULE_PATH)
topic_map = importlib.util.module_from_spec(SPEC)
sys.modules["topic_map"] = topic_map
SPEC.loader.exec_module(topic_map)


class TopicMapTests(unittest.TestCase):
    def write_page(self, root, rel_path, body):
        path = Path(root) / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def test_extract_page_removes_boilerplate_and_detects_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = self.write_page(
                root,
                "de/blog-posts/test.html",
                """
                <html>
                  <head>
                    <title>Test Titel | AXcent Dance</title>
                    <meta name="description" content="Eine Beschreibung">
                    <script type="application/ld+json">{"@context":"https://schema.org"}</script>
                  </head>
                  <body>
                    <header>Navigation should disappear</header>
                    <main>
                      <article>
                        <h1>Bachata Anfänger in Zürich</h1>
                        <p>Ein hilfreicher Artikel über Bachata für Anfänger.</p>
                        <a href="../schedule">Stundenplan</a>
                      </article>
                    </main>
                    <footer>Footer should disappear</footer>
                  </body>
                </html>
                """,
            )

            extracted = topic_map.extract_page(page, root)

            self.assertEqual(extracted.language, "de")
            self.assertEqual(extracted.page_type, "blog")
            self.assertIn("Bachata Anfänger", extracted.text)
            self.assertNotIn("Navigation should disappear", extracted.text)
            self.assertNotIn("Footer should disappear", extracted.text)
            self.assertIn("de/schedule", extracted.internal_links)

    def test_normalize_internal_link_supports_clean_urls_and_external_site_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                topic_map.normalize_internal_link_for_root("../schedule", "blog-posts/post.html", root),
                "schedule",
            )
            self.assertEqual(
                topic_map.normalize_internal_link_for_root("/de/beginner-guide", "de/blog-posts/post.html", root),
                "de/beginner-guide",
            )
            self.assertEqual(
                topic_map.normalize_internal_link_for_root(
                    "https://axcentdance.com/private-lessons#booking",
                    "blog-posts/post.html",
                    root,
                ),
                "private-lessons",
            )
            self.assertIsNone(
                topic_map.normalize_internal_link_for_root(
                    "https://example.com/private-lessons",
                    "blog-posts/post.html",
                    root,
                )
            )

    def test_cache_reuse_when_content_hash_matches(self):
        page = topic_map.PageData(
            path="beginner-guide.html",
            clean_path="beginner-guide",
            url="https://axcentdance.com/beginner-guide",
            language="en",
            page_type="guide",
            title="Beginner Guide",
            description="Guide description",
            h1="Beginner Guide",
            text="Helpful text",
            content_hash="abc123",
            internal_links=[],
            word_count=2,
        )
        cache = {
            "beginner-guide.html": {
                "model": topic_map.MODEL,
                "content_hash": "abc123",
                "embedding": [0.1, 0.2, 0.3],
            }
        }

        with patch.object(topic_map, "request_embeddings") as request_embeddings:
            embeddings = topic_map.ensure_embeddings([page], cache, refresh=False, api_key=None)

        request_embeddings.assert_not_called()
        self.assertEqual(embeddings["beginner-guide.html"], [0.1, 0.2, 0.3])

    def test_missing_api_key_exits_without_embedding_request(self):
        page = topic_map.PageData(
            path="beginner-guide.html",
            clean_path="beginner-guide",
            url="https://axcentdance.com/beginner-guide",
            language="en",
            page_type="guide",
            title="Beginner Guide",
            description="Guide description",
            h1="Beginner Guide",
            text="Helpful text",
            content_hash="abc123",
            internal_links=[],
            word_count=2,
        )

        with patch.object(topic_map, "request_embeddings") as request_embeddings:
            with self.assertRaises(SystemExit):
                topic_map.ensure_embeddings([page], {}, refresh=False, api_key=None)

        request_embeddings.assert_not_called()

    def test_recommendations_skip_existing_links(self):
        source = topic_map.PageData(
            path="blog-posts/start.html",
            clean_path="blog-posts/start",
            url="https://axcentdance.com/blog-posts/start",
            language="en",
            page_type="blog",
            title="Start Bachata",
            description="",
            h1="Start Bachata",
            text="",
            content_hash="source",
            internal_links=["beginner-guide"],
            word_count=600,
        )
        linked_target = topic_map.PageData(
            path="beginner-guide.html",
            clean_path="beginner-guide",
            url="https://axcentdance.com/beginner-guide",
            language="en",
            page_type="guide",
            title="Beginner Guide",
            description="",
            h1="Beginner Guide",
            text="",
            content_hash="target",
            internal_links=[],
            word_count=900,
        )
        unlinked_target = topic_map.PageData(
            path="schedule.html",
            clean_path="schedule",
            url="https://axcentdance.com/schedule",
            language="en",
            page_type="core",
            title="Schedule",
            description="",
            h1="Schedule",
            text="",
            content_hash="schedule",
            internal_links=[],
            word_count=500,
        )
        embeddings = {
            source.path: [1.0, 0.0],
            linked_target.path: [1.0, 0.0],
            unlinked_target.path: [0.95, 0.05],
        }

        suggestions = topic_map.build_link_suggestions(
            [source, linked_target, unlinked_target],
            embeddings,
            max_suggestions=10,
        )

        self.assertTrue(any(item.target == "schedule" for item in suggestions))
        self.assertFalse(
            any(item.source == "blog-posts/start" and item.target == "beginner-guide" for item in suggestions)
        )


if __name__ == "__main__":
    unittest.main()
