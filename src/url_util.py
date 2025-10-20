from urllib.parse import urljoin
import os


def build_url(*args):
    """Combines multiple URL parts into a single URL."""
    if not args:
        return ""

    base = args[0]
    base_with_trailing_slash = base if base[:-1] == "/" else f"{base}/"
    path = os.path.join(*args[1:])
    return urljoin(base_with_trailing_slash, path)
