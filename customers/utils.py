from urllib.parse import urlparse
from django.conf import settings

def is_safe_url(url, allowed_hosts=None):
    if allowed_hosts is None:
        allowed_hosts = {urlparse(settings.ALLOWED_HOSTS[0]).hostname}
    url_info = urlparse(url)
    return url_info.scheme in ('http', 'https') and url_info.hostname in allowed_hosts