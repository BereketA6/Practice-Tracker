"""
Looks up real song metadata (album art, preview clip, artist) from Apple's
iTunes Search API. This is free and requires no API key or auth — a good
fit for a student project since there's no billing/credentials to manage.

Docs: https://performance-partners.apple.com/search-api
"""

import requests

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"

# Simple in-memory cache so we don't hit the iTunes API on every single
# request for the same song. In a production app this would likely be
# Redis or a database table with a TTL; a plain dict is fine here since
# the data is static for the life of the server process.
_cache = {}


def lookup_song(title, artist=None, timeout=4):
    """
    Looks up a song on iTunes and returns a dict with artwork_url,
    preview_url, itunes_url, and artist_name — or None if no match
    was found or the request failed (e.g. no internet connection).

    We fail soft on purpose: a missing external API result should never
    break the suggestions feature, it should just mean no artwork/preview
    for that one entry.
    """
    cache_key = f"{title}|{artist or ''}"
    if cache_key in _cache:
        return _cache[cache_key]

    query = f"{title} {artist}" if artist else title

    try:
        response = requests.get(
            ITUNES_SEARCH_URL,
            params={"term": query, "media": "music", "entity": "song", "limit": 1},
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("resultCount", 0) == 0:
            _cache[cache_key] = None
            return None

        result = data["results"][0]

        # iTunes returns small 100x100 artwork by default; swapping the
        # size in the URL string gets a much better 300x300 image for free.
        artwork = result.get("artworkUrl100", "")
        artwork_large = artwork.replace("100x100bb", "300x300bb") if artwork else None

        song_info = {
            "artwork_url": artwork_large,
            "preview_url": result.get("previewUrl"),
            "itunes_url": result.get("trackViewUrl"),
            "artist_name": result.get("artistName"),
        }

        _cache[cache_key] = song_info
        return song_info

    except (requests.RequestException, ValueError, KeyError):
        # Network issue, timeout, or unexpected response shape — don't
        # crash the suggestions endpoint over it, just return nothing.
        _cache[cache_key] = None
        return None
