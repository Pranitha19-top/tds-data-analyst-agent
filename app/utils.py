import re

def extract_urls(text: str):
    """
    Extract all URLs from a given text string
    """
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    return urls
