import unittest

from src.URLUtils import getDomainName


# Test class
class URLUtilsTest(unittest.TestCase):

    def test_can_get_domain_names(self):
        self.assertEqual(getDomainName("https://www.google.com/"), "google")
        self.assertEqual(getDomainName("www.google.com/"), "google")
        self.assertEqual(getDomainName("https://www.google.co.uk"), "google")

    def test_works_with_capitals(self):
        self.assertEqual(getDomainName("https://www.BBC.co.uk/news"), "bbc")
        self.assertEqual(getDomainName("https://www.Imperial.ac.uk/"), "imperial")


# Running the tests
if __name__ == "__main__":
    unittest.main()
