import unittest

from src.URLUtils import getDomainName, isUrl


class URLUtilsTest(unittest.TestCase):

    def test_can_get_domain_names(self):
        self.assertEqual(getDomainName("https://www.google.com/"), "google")
        self.assertEqual(getDomainName("www.google.com/"), "google")
        self.assertEqual(getDomainName("https://www.google.co.uk"), "google")

    def test_works_with_capitals(self):
        self.assertEqual(getDomainName("https://www.BBC.co.uk/news"), "bbc")
        self.assertEqual(getDomainName("https://www.Imperial.ac.uk/"), "imperial")

    def test_returns_valid_urls(self):
        self.assertEqual(isUrl("https://www.google.com/"), "https://www.google.com/")
        self.assertEqual(isUrl("https://www.bbc.co.uk/news"), "https://www.bbc.co.uk/news")
        self.assertEqual(isUrl("http://www.imperial.ac.uk/"), "http://www.imperial.ac.uk/")

    def test_appends_https(self):
        self.assertEqual(isUrl("www.google.com"), "https://www.google.com")
        self.assertEqual(isUrl("www.bbc.co.uk/news"), "https://www.bbc.co.uk/news")
        self.assertEqual(isUrl("google.com"), "https://google.com")

    def test_turns_text_to_google_search(self):
        self.assertEqual(isUrl("google"), "https://www.google.com/search?q=google")
        self.assertEqual(isUrl("bbc news"), "https://www.google.com/search?q=bbc news")


if __name__ == "__main__":
    unittest.main()
