import unittest
from crawl import *

class TestCrawl(unittest.TestCase):
    def test_https_removal(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_slash_removal(self):
        input_url = "www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = 'www.boot.dev/blog/path'
        self.assertEqual(actual, expected)

    def test_https_slash_removal(self):
        input_url = "https://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = 'www.boot.dev/blog/path'
        self.assertEqual(actual, expected)

    def test_http_removal(self):
        input_url = "http://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_http_slash_removal(self):
        input_url = "http://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = 'www.boot.dev/blog/path'
        self.assertEqual(actual, expected)
#-----------------------------------------------------------#

    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h2(self):
        input_body = "<html><body><h2>Test Title</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_empty(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)
#-----------------------------------------------------------#

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_first_priority(self):
        input_body = """<html><body>
            <main>
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_empty(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_outside_main(self):
        input_body = """<html><body>
            <p>Only paragraph.</p>
            <main>
                <h1>Test Title</h1>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Only paragraph."
        self.assertEqual(actual, expected)
#-----------------------------------------------------------#

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/example/xyz.html"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/example/xyz.html"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_list(self):
        input_url = "https://crawler-test.com"
        input_body = '''<html><body>
            <a href="https://crawler-test.com"><span>Boot.dev</span></a>
            <a href="/example"><span>Boot.dev</span></a>
        </body></html>'''
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com", "https://crawler-test.com/example"]
        self.assertEqual(actual, expected)
#-----------------------------------------------------------#

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://crawler-test.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_list(self):
        input_url = "https://crawler-test.com"
        input_body = '''<html><body>
            <img src="https://crawler-test.com/logo.png" alt="Logo">
            <img src="/meme.png" alt="MeMe">
        </body></html>'''
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png", "https://crawler-test.com/meme.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_missing(self):
        input_url = "https://crawler-test.com"
        input_body = '''<html><body>
            <a href="/example/xyz.html"><span>Boot.dev</span></a>
        </body></html>'''
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)
#-----------------------------------------------------------#

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_empty(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body></body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
