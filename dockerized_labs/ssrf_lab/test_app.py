import unittest

from dockerized_labs.ssrf_lab.app import app


class BlogReaderTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_listed_blog_can_be_read(self):
        response = self.client.post("/lab1", data={"blog": "blog1"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Top 10 community survey", response.data)

    def test_file_paths_are_rejected(self):
        for path in ("app.py", "../.env", "blogs/blog1.txt"):
            with self.subTest(path=path):
                response = self.client.post("/lab1", data={"blog": path})

                self.assertEqual(response.status_code, 200)
                self.assertIn(b"No blog found", response.data)


if __name__ == "__main__":
    unittest.main()
