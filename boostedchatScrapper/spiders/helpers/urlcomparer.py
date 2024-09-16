from urllib.parse import urlparse
from difflib import SequenceMatcher

class URLComparer:
    def __init__(self, list1, list2):
        self.list1 = list1
        self.list2 = list2

    def parse_url(self, url):
        """
        Parse URL to extract its domain and path.
        """
        parsed_url = urlparse(url)
        return parsed_url.netloc, parsed_url.path

    def find_missing_urls(self):
        """
        Find URLs in list1 that are missing in list2.
        """
        missing_urls = [url for url in self.list1 if url not in self.list2]
        return missing_urls

    def find_similar_urls(self, threshold=1.0):
        """
        Find URLs in list1 that are similar to URLs in list2.
        """
        similar_urls = []
        for url1 in self.list1:
            for url2 in self.list2:
                domain1, path1 = self.parse_url(url1)
                domain2, path2 = self.parse_url(url2)
                if domain1 == domain2:
                    similarity = SequenceMatcher(None, path1, path2).ratio()
                    if similarity >= threshold:
                        similar_urls.append((url1, url2, similarity))
        return similar_urls

# Example usage:
list1 = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]
list2 = ["https://example.com/page1", "https://example.com/page4", "https://example.com/page5"]

url_comparer = URLComparer(list1, list2)

missing_urls = url_comparer.find_missing_urls()
print("Missing URLs:", missing_urls)

similar_urls = url_comparer.find_similar_urls()
print("Similar URLs:", similar_urls)
