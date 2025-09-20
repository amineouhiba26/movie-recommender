import pandas as pd
import numpy as np
import json
import joblib
from difflib import get_close_matches
from typing import List, Dict, Tuple, Optional

class MovieRecommender:
    """
    Robust movie recommendation system using precomputed similarity matrix
    """
    
    def __init__(self, artifacts_path="artifacts"):
        """Initialize recommender with saved artifacts"""
        self.artifacts_path = artifacts_path
        self.df = None
        self.similarity_matrix = None
        self.metadata = None
        self.title_to_idx = {}
        self.id_to_idx = {}
        self.load_artifacts()
    
    def load_artifacts(self):
        """Load all preprocessing artifacts"""
        try:
            print("Loading preprocessed data...")
            
            # Load dataframe
            self.df = pd.read_csv(f"{self.artifacts_path}/movies_preprocessed.csv")
            
            # Load similarity matrix
            self.similarity_matrix = np.load(f"{self.artifacts_path}/similarity_matrix.npy")
            
            # Load metadata
            with open(f"{self.artifacts_path}/metadata.json", "r") as f:
                self.metadata = json.load(f)
            
            # Create lookup dictionaries
            self.title_to_idx = {title.lower().strip(): idx for idx, title in enumerate(self.df["title_normalized"])}
            self.id_to_idx = {movie_id: idx for idx, movie_id in enumerate(self.df["id"])}
            
            print(f"Loaded {len(self.df)} movies successfully")
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Artifacts not found. Please run preprocess_movies.py first. Error: {e}")
        except Exception as e:
            raise Exception(f"Error loading artifacts: {e}")
    
    def find_movie_by_title(self, title: str, max_matches=5) -> List[Tuple[str, int, float]]:
        """
        Find movies by title with fuzzy matching
        Returns list of (title, movie_id, similarity_score) tuples
        """
        title_normalized = title.lower().strip()
        
        # Exact match first
        if title_normalized in self.title_to_idx:
            idx = self.title_to_idx[title_normalized]
            return [(self.df.iloc[idx]["title"], int(self.df.iloc[idx]["id"]), 1.0)]
        
        # Fuzzy matching
        possible_matches = get_close_matches(
            title_normalized, 
            self.title_to_idx.keys(), 
            n=max_matches, 
            cutoff=0.3
        )
        
        results = []
        for match in possible_matches:
            idx = self.title_to_idx[match]
            # Calculate similarity score based on string matching
            similarity = len(set(title_normalized.split()) & set(match.split())) / len(set(title_normalized.split()) | set(match.split()))
            results.append((self.df.iloc[idx]["title"], int(self.df.iloc[idx]["id"]), similarity))
        
        return results
    
    def get_movie_info(self, movie_id: int) -> Optional[Dict]:
        """Get detailed information about a movie by ID"""
        if movie_id not in self.id_to_idx:
            return None
        
        idx = self.id_to_idx[movie_id]
        movie = self.df.iloc[idx]
        
        # Parse genres properly
        genres = movie["genres"]
        if isinstance(genres, str):
            try:
                genres = eval(genres)
            except:
                genres = [genres]
        elif pd.isna(genres):
            genres = []
        
        return {
            "id": int(movie["id"]),
            "title": movie["title"],
            "genres": genres,
            "overview": movie["overview"],
            "vote_average": float(movie["vote_average"]),
            "vote_count": int(movie["vote_count"]),
            "release_date": movie.get("release_date", "Unknown")
        }
    
    def recommend_by_movie_id(self, movie_id: int, num_recommendations=10) -> List[Dict]:
        """
        Get recommendations based on movie ID
        """
        if movie_id not in self.id_to_idx:
            raise ValueError(f"Movie ID {movie_id} not found in dataset")
        
        movie_idx = self.id_to_idx[movie_id]
        
        # Get similarity scores
        similarity_scores = self.similarity_matrix[movie_idx]
        
        # Get indices sorted by similarity (excluding the movie itself)
        similar_indices = np.argsort(similarity_scores)[::-1][1:num_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            movie = self.df.iloc[idx]
            
            # Parse genres properly
            genres = movie["genres"]
            if isinstance(genres, str):
                try:
                    genres = eval(genres)
                except:
                    genres = [genres]
            elif pd.isna(genres):
                genres = []
            
            recommendations.append({
                "id": int(movie["id"]),
                "title": movie["title"],
                "genres": genres,
                "overview": movie["overview"],
                "vote_average": float(movie["vote_average"]),
                "vote_count": int(movie["vote_count"]),
                "similarity_score": float(similarity_scores[idx]),
                "release_date": movie.get("release_date", "Unknown")
            })
        
        return recommendations
    
    def recommend_by_title(self, title: str, num_recommendations=10) -> Dict:
        """
        Get recommendations based on movie title
        Returns dict with matched movies and recommendations
        """
        # Find matching movies
        matches = self.find_movie_by_title(title)
        
        if not matches:
            return {
                "error": f"No movies found matching '{title}'",
                "suggestions": []
            }
        
        # Use the best match
        best_match = matches[0]
        movie_id = best_match[1]
        
        # Get recommendations
        recommendations = self.recommend_by_movie_id(movie_id, num_recommendations)
        
        return {
            "query": title,
            "matched_movie": self.get_movie_info(movie_id),
            "other_matches": [{"title": m[0], "id": m[1], "score": m[2]} for m in matches[1:]] if len(matches) > 1 else [],
            "recommendations": recommendations
        }
    
    def get_random_movies(self, num_movies=5) -> List[Dict]:
        """Get random movies for exploration"""
        random_indices = np.random.choice(len(self.df), size=min(num_movies, len(self.df)), replace=False)
        
        movies = []
        for idx in random_indices:
            movie = self.df.iloc[idx]
            
            # Parse genres properly
            genres = movie["genres"]
            if isinstance(genres, str):
                try:
                    genres = eval(genres)
                except:
                    genres = [genres]
            elif pd.isna(genres):
                genres = []
            
            movies.append({
                "id": int(movie["id"]),
                "title": movie["title"],
                "genres": genres,
                "overview": movie["overview"],
                "vote_average": float(movie["vote_average"]),
                "vote_count": int(movie["vote_count"]),
                "release_date": movie.get("release_date", "Unknown")
            })
        
        return movies
    
    def search_by_genre(self, genre: str, limit=20) -> List[Dict]:
        """Search movies by genre"""
        genre_movies = []
        
        for idx, row in self.df.iterrows():
            # Parse genres properly
            movie_genres = row["genres"]
            if isinstance(movie_genres, str):
                try:
                    movie_genres = eval(movie_genres)
                except:
                    movie_genres = [movie_genres]
            elif pd.isna(movie_genres):
                movie_genres = []
            
            if any(genre.lower() in g.lower() for g in movie_genres):
                genre_movies.append({
                    "id": int(row["id"]),
                    "title": row["title"],
                    "genres": movie_genres,
                    "overview": row["overview"],
                    "vote_average": float(row["vote_average"]),
                    "vote_count": int(row["vote_count"]),
                    "release_date": row.get("release_date", "Unknown")
                })
        
        # Sort by rating and vote count
        genre_movies.sort(key=lambda x: (x["vote_average"], x["vote_count"]), reverse=True)
        
        return genre_movies[:limit]
    
    def get_stats(self) -> Dict:
        """Get dataset statistics"""
        return {
            "total_movies": len(self.df),
            "unique_genres": self.metadata.get("unique_genres", []),
            "avg_rating": float(self.df["vote_average"].mean()),
            "feature_dimensions": self.metadata.get("feature_dimensions", 0)
        }

if __name__ == "__main__":
    # Test the recommender
    recommender = MovieRecommender()
    
    # Test with a known movie
    print("Testing recommendations for 'Interstellar':")
    result = recommender.recommend_by_title("Interstellar", 5)
    
    if "error" not in result:
        print(f"Matched: {result['matched_movie']['title']}")
        print("\nRecommendations:")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"{i}. {rec['title']} (Score: {rec['similarity_score']:.3f})")
    else:
        print(result["error"])
