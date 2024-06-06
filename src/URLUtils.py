import tldextract
import re


def getDomainName(url):
    extracted = tldextract.extract(url)
    return extracted.domain.lower()


def isUrl(url):
    text = url

    url_regex = re.compile(
        r'^(https?:\/\/)' 
        r'((([a-zA-Z\d]([a-zA-Z\d-]*[a-zA-Z\d])*)\.)+[a-zA-Z]{2,}|'  
        r'((\d{1,3}\.){3}\d{1,3}))'  
        r'(\:\d+)?(\/[-a-zA-Z\d%_.~+]*)*'  
        r'(\?[;&a-zA-Z\d%_.~+=-]*)?' 
        r'(\#[-a-zA-Z\d_]*)?$'
    )

    if re.match(url_regex, text):
        return text

    if not text.startswith('http://') and not text.startswith('https://'):
        text = 'https://' + text

    if re.match(url_regex, text):
        return text

    return "https://www.google.com/search?q=" + url
