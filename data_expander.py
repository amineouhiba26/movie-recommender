#!/usr/bin/env python3
"""
Expandeur de base de données de films
Permet d'élargir le dataset en récupérant des films depuis plusieurs sources
"""

import json
import requests
import time
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path

class MovieDataExpander:
    """Classe pour élargir la base de données de films"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.current_movies = self.load_current_dataset()
        
    def load_current_dataset(self) -> List[Dict]:
        """Charge le dataset actuel"""
        try:
            with open('movies_dataset.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def get_popular_movies(self, pages: int = 5) -> List[Dict]:
        """Récupère les films populaires depuis TMDB"""
        if not self.api_key:
            print("⚠️  Clé API TMDB non fournie. Utilisation du dataset limité.")
            return []
        
        movies = []
        for page in range(1, pages + 1):
            try:
                url = f"{self.tmdb_base_url}/movie/popular"
                params = {
                    'api_key': self.api_key,
                    'page': page,
                    'language': 'fr-FR'
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for movie in data['results']:
                    if self._is_valid_movie(movie):
                        processed_movie = self._process_tmdb_movie(movie)
                        if processed_movie:
                            movies.append(processed_movie)
                
                # Respecter les limites d'API
                time.sleep(0.25)
                print(f"📥 Page {page}/{pages} récupérée: {len(data['results'])} films")
                
            except Exception as e:
                print(f"❌ Erreur lors de la récupération de la page {page}: {e}")
                continue
        
        return movies
    
    def get_movies_by_genre(self, genre_id: int, pages: int = 3) -> List[Dict]:
        """Récupère des films par genre"""
        if not self.api_key:
            return []
        
        movies = []
        for page in range(1, pages + 1):
            try:
                url = f"{self.tmdb_base_url}/discover/movie"
                params = {
                    'api_key': self.api_key,
                    'with_genres': genre_id,
                    'page': page,
                    'language': 'fr-FR',
                    'sort_by': 'vote_average.desc',
                    'vote_count.gte': 100
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for movie in data['results']:
                    if self._is_valid_movie(movie):
                        processed_movie = self._process_tmdb_movie(movie)
                        if processed_movie:
                            movies.append(processed_movie)
                
                time.sleep(0.25)
                
            except Exception as e:
                print(f"❌ Erreur genre {genre_id}, page {page}: {e}")
                continue
        
        return movies
    
    def expand_dataset(self, target_size: int = 500) -> List[Dict]:
        """Élargit le dataset jusqu'à la taille cible"""
        print(f"🎬 Expansion du dataset vers {target_size} films...")
        
        all_movies = self.current_movies.copy()
        current_size = len(all_movies)
        
        if current_size >= target_size:
            print(f"✅ Dataset déjà suffisant: {current_size} films")
            return all_movies
        
        # Genres populaires TMDB
        genres = {
            28: "Action", 18: "Drame", 35: "Comédie", 80: "Crime",
            14: "Fantastique", 27: "Horreur", 10749: "Romance",
            878: "Science-Fiction", 53: "Thriller", 12: "Aventure"
        }
        
        # Récupérer films populaires
        popular_movies = self.get_popular_movies(pages=10)
        all_movies.extend(popular_movies)
        
        # Récupérer par genre si nécessaire
        for genre_id, genre_name in genres.items():
            if len(all_movies) >= target_size:
                break
            
            print(f"🎭 Récupération films {genre_name}...")
            genre_movies = self.get_movies_by_genre(genre_id, pages=2)
            all_movies.extend(genre_movies)
        
        # Déduplication
        unique_movies = self._deduplicate_movies(all_movies)
        
        print(f"✅ Dataset élargi: {len(unique_movies)} films uniques")
        return unique_movies[:target_size]
    
    def _is_valid_movie(self, movie: Dict) -> bool:
        """Vérifie si un film est valide pour notre dataset"""
        return (
            movie.get('overview') and 
            len(movie.get('overview', '')) > 50 and
            movie.get('vote_average', 0) > 0 and
            movie.get('vote_count', 0) > 10 and
            movie.get('release_date', '')
        )
    
    def _process_tmdb_movie(self, movie: Dict) -> Optional[Dict]:
        """Traite un film TMDB vers notre format"""
        try:
            # Récupérer les détails complets du film
            if self.api_key:
                details = self._get_movie_details(movie['id'])
                if details:
                    genres = [g['name'] for g in details.get('genres', [])]
                else:
                    genres = []
            else:
                genres = []
            
            return {
                'id': movie['id'],
                'title': movie['title'],
                'genres': genres,
                'overview': movie['overview'],
                'vote_average': round(movie['vote_average'], 1),
                'vote_count': movie['vote_count'],
                'release_date': movie['release_date'],
                'popularity': round(movie.get('popularity', 0), 1)
            }
        except Exception as e:
            print(f"❌ Erreur traitement film {movie.get('title', 'Unknown')}: {e}")
            return None
    
    def _get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Récupère les détails complets d'un film"""
        try:
            url = f"{self.tmdb_base_url}/movie/{movie_id}"
            params = {
                'api_key': self.api_key,
                'language': 'fr-FR'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except Exception:
            return None
    
    def _deduplicate_movies(self, movies: List[Dict]) -> List[Dict]:
        """Supprime les doublons basés sur l'ID"""
        seen_ids = set()
        unique_movies = []
        
        for movie in movies:
            if movie['id'] not in seen_ids:
                seen_ids.add(movie['id'])
                unique_movies.append(movie)
        
        return unique_movies
    
    def save_expanded_dataset(self, movies: List[Dict], filename: str = 'movies_dataset_expanded.json'):
        """Sauvegarde le dataset élargi"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Dataset sauvegardé: {filename} ({len(movies)} films)")
    
    def create_sample_expansion(self) -> List[Dict]:
        """Crée une expansion échantillon sans API"""
        print("🎬 Création d'une expansion échantillon...")
        
        # Films échantillon pour démonstration
        sample_movies = [
            {
                "id": 999001,
                "title": "Dune",
                "genres": ["Science-Fiction", "Aventure", "Drame"],
                "overview": "L'histoire de Paul Atreides, jeune homme aussi brillant que talentueux, voué à connaître un destin hors du commun qui le dépasse totalement.",
                "vote_average": 8.1,
                "vote_count": 8934,
                "release_date": "2021-09-15",
                "popularity": 42.8
            },
            {
                "id": 999002,
                "title": "Spider-Man: No Way Home",
                "genres": ["Action", "Aventure", "Science-Fiction"],
                "overview": "Peter Parker est démasqué et ne peut plus séparer sa vie normale des enjeux de son statut de super-héros.",
                "vote_average": 8.4,
                "vote_count": 15234,
                "release_date": "2021-12-15",
                "popularity": 98.3
            },
            {
                "id": 999003,
                "title": "The Batman",
                "genres": ["Crime", "Drame", "Thriller"],
                "overview": "Dans sa deuxième année de lutte contre le crime, Batman explore la corruption qui sévit à Gotham City.",
                "vote_average": 7.8,
                "vote_count": 12456,
                "release_date": "2022-03-04",
                "popularity": 87.4
            }
        ]
        
        return self.current_movies + sample_movies

def main():
    """Fonction principale pour l'expansion du dataset"""
    expander = MovieDataExpander()
    
    print("🎬 Expandeur de Base de Données de Films")
    print("=====================================")
    
    choice = input("""
Choisissez une option:
1. Expansion échantillon (sans API)
2. Expansion complète (nécessite clé TMDB)
3. Quitter

Votre choix (1-3): """).strip()
    
    if choice == "1":
        expanded_movies = expander.create_sample_expansion()
        expander.save_expanded_dataset(expanded_movies)
        
    elif choice == "2":
        api_key = input("Entrez votre clé API TMDB: ").strip()
        if api_key:
            expander.api_key = api_key
            target_size = int(input("Taille cible du dataset (défaut: 500): ") or "500")
            
            expanded_movies = expander.expand_dataset(target_size)
            expander.save_expanded_dataset(expanded_movies)
        else:
            print("❌ Clé API requise pour l'expansion complète")
    
    elif choice == "3":
        print("👋 À bientôt!")
        return
    
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    main()
