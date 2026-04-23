from __future__ import annotations

from urllib.parse import urlparse


def normalize_organization(organization: str) -> str:
    value = organization.strip().rstrip("/")
    if not value:
        return ""

    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = parsed.netloc.lower()
    path_segments = [segment for segment in parsed.path.split("/") if segment]

    if host.endswith(".visualstudio.com"):
        return host.split(".")[0]
    if host == "dev.azure.com" and path_segments:
        first_segment = path_segments[0]
        if first_segment.startswith("http"):
            nested = normalize_organization("/".join(path_segments))
            if nested:
                return nested
        return first_segment

    if ".visualstudio.com" in value:
        return value.split(".visualstudio.com")[0].split("/")[-1]
    if "dev.azure.com/" in value:
        return value.split("dev.azure.com/", 1)[1].split("/", 1)[0]

    return value


def base_url(organization: str) -> str:
    return f"https://dev.azure.com/{normalize_organization(organization)}"
