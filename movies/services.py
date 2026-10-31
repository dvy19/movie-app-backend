import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {settings.TMDB_ACCESS_TOKEN}"
}


def get_movies(endpoint, params=None):

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=HEADERS,
        params=params,
        timeout=15,
        verify=False
    )

    response.raise_for_status()

    return response.json()