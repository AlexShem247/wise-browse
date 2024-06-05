import tldextract


def getDomainName(url):
    extracted = tldextract.extract(url)
    return extracted.domain.lower()
