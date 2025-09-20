import os
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# Base URL for TMDB API
BASE_URL = "https://api.themoviedb.org/3"

def get_popular_movies(page=1):
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "page": page
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print("Error fetching data:", response.status_code, response.text)
        return []

if __name__ == "__main__":
    movies = get_popular_movies()
    print("🎬 Popular movies:")
    for movie in movies[:10]:  # print first 10
        print(f"{movie['title']} ({movie['release_date']})")
