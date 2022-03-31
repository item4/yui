import base64
from urllib.parse import urlencode


def b64_redirect(url: str) -> str:
    """Redirect helper for non-http protocols."""

    return "https://item4.github.io/yui/helpers/b64-redirect.html?{}".format(
        urlencode({"b64": base64.urlsafe_b64encode(url.encode()).decode()})
    )
