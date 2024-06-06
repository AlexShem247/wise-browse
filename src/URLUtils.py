import tldextract
import re


def getDomainName(url):
    extracted = tldextract.extract(url)
    return extracted.domain.lower()


def isUrl(text):
    # Regular expression to match URLs with mandatory scheme (http or https)
    url_regex = re.compile(
        r'^(https?:\/\/)'  # Mandatory scheme (http or https)
        r'((([a-zA-Z\d]([a-zA-Z\d-]*[a-zA-Z\d])*)\.)+[a-zA-Z]{2,}|'  # Domain name
        r'((\d{1,3}\.){3}\d{1,3}))'  # OR IPv4 address
        r'(\:\d+)?(\/[-a-zA-Z\d%_.~+]*)*'  # Optional port and path
        r'(\?[;&a-zA-Z\d%_.~+=-]*)?'  # Optional query string
        r'(\#[-a-zA-Z\d_]*)?$'  # Optional fragment
    )

    # Check if the text matches the URL pattern
    if re.match(url_regex, text):
        return text

    # If no scheme, prepend 'https://'
    if not text.startswith('http://') and not text.startswith('https://'):
        text = 'https://' + text

    # Recheck with the prepended scheme
    if re.match(url_regex, text):
        return text

    # If it still doesn't match, it's not a valid URL
    return None
