"""
Data loader for the MovieLens + optional TMDB enrichment
File: data/load_movielens.py

What this script does:
- Download MovieLens `ml-latest-small` (if not already present) from GroupLens.
- Extract CSV files and load `movies.csv` and `ratings.csv` into pandas DataFrames.
- Do light preprocessing on movie titles (extract year, clean title).
- Optionally enrich movies with TMDB overviews (requires TMDB_API_KEY environment variable).
- Cache TMDB responses to `data/tmdb_cache.json` to avoid repeated API calls and rate limits.

Usage (examples):
    python data/load_movielens.py --download
    python data/load_movielens.py --stats
    python data/load_movielens.py --enrich-tmdb

Notes:
- This file is intended to be run inside your project root (where you will create a `data/` folder).
- Do not commit your TMDB API key to a public repository. Use environment variables.

"""

import os
import re
import json
import argparse
import zipfile
from pathlib import Path
from typing import Tuple, Optional

import pandas as pd
import requests

# stable MovieLens ml-latest-small URL
MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"

DATA_DIR = Path("data")
ML_DIR = DATA_DIR / "ml-latest-small"
ZIP_PATH = DATA_DIR / "ml-latest-small.zip"
TMDB_CACHE = DATA_DIR / "tmdb_cache.json"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_movielens(dest_zip: Path = ZIP_PATH, url: str = MOVIELENS_URL, force: bool = False) -> Path:
    """Download the MovieLens zip file if not already present.

    Returns the path to the downloaded zip file.
    """
    ensure_data_dir()
    if dest_zip.exists() and not force:
        print(f"MovieLens zip already exists at {dest_zip}")
        return dest_zip

    print(f"Downloading MovieLens from {url} -> {dest_zip} ...")
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()

    with open(dest_zip, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print("Download finished.")
    return dest_zip


def extract_zip(zip_path: Path = ZIP_PATH, extract_to: Path = ML_DIR) -> Path:
    """Extract the MovieLens zip file to the data directory. Returns extracted dir."""
    ensure_data_dir()
    if extract_to.exists():
        print(f"MovieLens already extracted to {extract_to}")
        return extract_to

    print(f"Extracting {zip_path} to {extract_to} ...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(DATA_DIR)
    print("Extraction finished.")
    return extract_to


def load_movielens(data_folder: Path = ML_DIR) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load movies.csv and ratings.csv into DataFrames.

    Returns (movies_df, ratings_df)
    """
    movies_path = data_folder / "movies.csv"
    ratings_path = data_folder / "ratings.csv"

    if not movies_path.exists() or not ratings_path.exists():
        raise FileNotFoundError("movies.csv or ratings.csv not found. Run --download first.")

    movies = pd.read_csv(movies_path)
    ratings = pd.read_csv(ratings_path)

    # light preprocessing on titles
    movies = preprocess_movies(movies)

    return movies, ratings


def preprocess_movies(movies: pd.DataFrame) -> pd.DataFrame:
    """Add columns: title_clean, year, title_no_year

    MovieLens titles often include the year in parentheses, e.g. "Toy Story (1995)".
    We extract that year into a separate column and a cleaned title for further text processing.
    """
    def extract_year(title: str) -> Optional[int]:
        m = re.search(r"\((\d{4})\)", str(title))
        if m:
            try:
                return int(m.group(1))
            except:
                return None
        return None

    movies = movies.copy()
    movies['year'] = movies['title'].apply(extract_year)
    # title without year
    movies['title_no_year'] = movies['title'].apply(lambda t: re.sub(r"\s*\(\d{4}\)\s*", "", str(t)))
    # simple cleaning for text processing
    movies['title_clean'] = movies['title_no_year'].str.lower().str.replace('[^a-z0-9 ]', ' ', regex=True).str.replace('\s+', ' ', regex=True).str.strip()

    # combine genres and title for a basic content field
    movies['content'] = movies['title_clean'] + ' ' + movies['genres'].str.replace('|', ' ')
    return movies


# ---------------- TMDB enrichment (optional) ----------------

def load_tmdb_cache(cache_path: Path = TMDB_CACHE) -> dict:
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_tmdb_cache(cache: dict, cache_path: Path = TMDB_CACHE):
    ensure_data_dir()
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')


def tmdb_search_movie(title: str, year: Optional[int], tmdb_api_key: str) -> Optional[dict]:
    """Search TMDB for a movie by title and optional year. Returns the first result or None."""
    if not tmdb_api_key:
        raise ValueError("TMDB API key is required")

    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": tmdb_api_key, "query": title}
    if year:
        params['year'] = int(year)

    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        return None
    data = resp.json()
    results = data.get('results', [])
    if not results:
        return None
    return results[0]


def enrich_movies_with_tmdb(movies: pd.DataFrame, tmdb_api_key: Optional[str] = None, cache_path: Path = TMDB_CACHE) -> pd.DataFrame:
    """Enrich movies DataFrame with TMDB overview (if available). Uses a local cache to avoid repeated requests."""
    if tmdb_api_key is None:
        tmdb_api_key = os.getenv('TMDB_API_KEY')

    if not tmdb_api_key:
        print("TMDB API key not provided. Skipping enrichment.")
        movies['overview'] = None
        return movies

    cache = load_tmdb_cache(cache_path)

    overviews = []
    for idx, row in movies.iterrows():
        key = f"{row['title_no_year']}|{row['year']}"
        if key in cache:
            overviews.append(cache[key].get('overview'))
            continue

        # try search
        try:
            res = tmdb_search_movie(row['title_no_year'], row['year'], tmdb_api_key)
            if res and 'overview' in res:
                cache[key] = {'overview': res['overview'], 'tmdb_id': res.get('id')}
                overviews.append(res['overview'])
            else:
                cache[key] = {'overview': None}
                overviews.append(None)
        except Exception as e:
            print(f"TMDB request failed for {row['title_no_year']}: {e}")
            cache[key] = {'overview': None}
            overviews.append(None)

    movies = movies.copy()
    movies['overview'] = overviews
    save_tmdb_cache(cache, cache_path)
    return movies


# ---------------- CLI / main ----------------

def print_stats(movies: pd.DataFrame, ratings: pd.DataFrame):
    print("\nMovieLens dataset stats:")
    print(f" - movies: {len(movies)}")
    print(f" - ratings: {len(ratings)}")
    users = ratings['userId'].nunique() if 'userId' in ratings.columns else ratings['user_id'].nunique()
    print(f" - unique users: {users}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true', help='Download and extract MovieLens ml-latest-small')
    parser.add_argument('--enrich-tmdb', action='store_true', help='Enrich movies with TMDB overviews (requires TMDB_API_KEY env var)')
    parser.add_argument('--stats', action='store_true', help='Print dataset stats after loading')
    args = parser.parse_args()

    if args.download:
        zip_path = download_movielens()
        extract_zip(zip_path)

    try:
        movies, ratings = load_movielens()
    except FileNotFoundError:
        print('MovieLens data not found. Run with --download first.')
        return

    if args.enrich_tmdb or args.enrich_tmdb if False else args.enrich_tmdb:
        tmdb_key = os.getenv('TMDB_API_KEY')
        movies = enrich_movies_with_tmdb(movies, tmdb_api_key=tmdb_key)
        print('TMDB enrichment finished (cached).')

    if args.stats:
        print_stats(movies, ratings)

    # small demo output
    print('\nSample movies (first 10):')
    print(movies[['movieId', 'title', 'year']].head(10).to_string(index=False))


if __name__ == '__main__':
    main()
