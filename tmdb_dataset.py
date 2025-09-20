import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def get_popular_movies(page=1):
    """Fetch popular movies list from TMDB"""
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
        print("Error:", response.status_code, response.text)
        return []

def get_movie_details(movie_id):
    """Fetch detailed movie info"""
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching movie", movie_id)
        return {}

def build_dataset(pages=2):
    """Build dataset with multiple popular pages"""
    dataset = []
    for page in range(1, pages+1):
        movies = get_popular_movies(page)
        for movie in movies:
            details = get_movie_details(movie["id"])
            dataset.append({
                "id": details.get("id"),
                "title": details.get("title"),
                "genres": [g["name"] for g in details.get("genres", [])],
                "overview": details.get("overview"),
                "release_date": details.get("release_date"),
                "vote_average": details.get("vote_average"),
                "vote_count": details.get("vote_count")
            })
    # Save to JSON file
    with open("movies_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"Dataset saved with {len(dataset)} movies!")

if __name__ == "__main__":
    build_dataset(pages=10)  
