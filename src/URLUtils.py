import tldextract
import re


def getDomainName(url):
    extracted = tldextract.extract(url)
    return extracted.domain.lower()


def formatHtml(text):
    # Regular expression to find lines starting with ###
    pattern = re.compile(r'^(###\s*)(.*)', re.MULTILINE)

    # Replace the pattern with the HTML <h2> tag
    text = pattern.sub(r'<h2>\2</h2>', text)

    # Regular expression to find text enclosed in **
    bold_pattern = re.compile(r'\*\*(.*?)\*\*')
    # Replace the pattern with the HTML <b> tag
    text = bold_pattern.sub(r'<b>\1</b>', text)

    text = text.replace("\n", "<br>")

    return text


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
