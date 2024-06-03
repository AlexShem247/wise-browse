from urllib.parse import urlparse


def getDomainName(url):
    # Add https part to url if missing
    if url[:3] == "www":
        url = "https://" + url

    parsed_url = urlparse(url.lower())
    domain = parsed_url.netloc
    parts = domain.split(".")

    if parts[0] == "www" and len(parts) > 1:
        return parts[1]
    else:
        return parts[0]