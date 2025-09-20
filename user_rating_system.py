#!/usr/bin/env python3
"""
Système de notation et retour utilisateur
Permet aux utilisateurs de noter des films et d'améliorer les recommandations
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd

class UserRatingSystem:
    """Système de gestion des notes et retours utilisateurs"""
    
    def __init__(self, db_path: str = "user_ratings.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferences TEXT  -- JSON des préférences
            )
        ''')
        
        # Table des notes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                movie_id INTEGER,
                rating REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, movie_id)
            )
        ''')
        
        # Table des retours sur recommandations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendation_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                movie_id INTEGER,
                recommended_movie_id INTEGER,
                feedback TEXT,  -- 'like', 'dislike', 'not_interested'
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Table des interactions utilisateur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                movie_id INTEGER,
                interaction_type TEXT,  -- 'view', 'search', 'recommend'
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée")
    
    def create_user(self, user_id: str, preferences: Optional[Dict] = None) -> bool:
        """Crée un nouvel utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            prefs_json = json.dumps(preferences or {})
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, preferences) VALUES (?, ?)",
                (user_id, prefs_json)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {e}")
            return False
    
    def add_rating(self, user_id: str, movie_id: int, rating: float) -> bool:
        """Ajoute une note d'utilisateur"""
        if not (0 <= rating <= 10):
            raise ValueError("La note doit être entre 0 et 10")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Créer l'utilisateur s'il n'existe pas
            self.create_user(user_id)
            
            cursor.execute('''
                INSERT OR REPLACE INTO ratings (user_id, movie_id, rating)
                VALUES (?, ?, ?)
            ''', (user_id, movie_id, rating))
            
            conn.commit()
            conn.close()
            print(f"✅ Note ajoutée: {rating}/10 pour le film {movie_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur ajout note: {e}")
            return False
    
    def delete_rating(self, user_id: str, movie_id: int) -> bool:
        """Supprime une note d'utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM ratings 
                WHERE user_id = ? AND movie_id = ?
            ''', (user_id, movie_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"✅ Note supprimée pour le film {movie_id}")
                return True
            else:
                conn.close()
                print(f"⚠️ Aucune note trouvée pour le film {movie_id}")
                return False
            
        except Exception as e:
            print(f"❌ Erreur suppression note: {e}")
            return False
    
    def get_user_ratings(self, user_id: str) -> List[Tuple[int, float]]:
        """Récupère toutes les notes d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT movie_id, rating FROM ratings WHERE user_id = ?",
                (user_id,)
            )
            
            ratings = cursor.fetchall()
            conn.close()
            return ratings
            
        except Exception as e:
            print(f"❌ Erreur récupération notes: {e}")
            return []
    
    def add_recommendation_feedback(self, user_id: str, movie_id: int, 
                                  recommended_movie_id: int, feedback: str) -> bool:
        """Ajoute un retour sur une recommandation"""
        valid_feedback = ['like', 'dislike', 'not_interested', 'watched']
        if feedback not in valid_feedback:
            raise ValueError(f"Feedback doit être dans: {valid_feedback}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            self.create_user(user_id)
            
            cursor.execute('''
                INSERT INTO recommendation_feedback 
                (user_id, movie_id, recommended_movie_id, feedback)
                VALUES (?, ?, ?, ?)
            ''', (user_id, movie_id, recommended_movie_id, feedback))
            
            conn.commit()
            conn.close()
            print(f"✅ Retour enregistré: {feedback}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur ajout retour: {e}")
            return False
    
    def log_interaction(self, user_id: str, movie_id: int, interaction_type: str) -> bool:
        """Enregistre une interaction utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            self.create_user(user_id)
            
            cursor.execute('''
                INSERT INTO user_interactions (user_id, movie_id, interaction_type)
                VALUES (?, ?, ?)
            ''', (user_id, movie_id, interaction_type))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erreur log interaction: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Analyse les préférences utilisateur basées sur ses notes"""
        ratings = self.get_user_ratings(user_id)
        
        if not ratings:
            return {}
        
        # Charger les films pour analyser les genres
        try:
            with open('movies_dataset.json', 'r', encoding='utf-8') as f:
                movies = json.load(f)
            
            movies_dict = {movie['id']: movie for movie in movies}
        except:
            return {}
        
        genre_scores = {}
        total_ratings = 0
        
        for movie_id, rating in ratings:
            if movie_id in movies_dict:
                movie = movies_dict[movie_id]
                for genre in movie.get('genres', []):
                    if genre not in genre_scores:
                        genre_scores[genre] = []
                    genre_scores[genre].append(rating)
                total_ratings += 1
        
        # Calculer les scores moyens par genre
        preferences = {}
        for genre, scores in genre_scores.items():
            avg_score = sum(scores) / len(scores)
            preferences[genre] = {
                'average_rating': round(avg_score, 2),
                'count': len(scores),
                'preference_score': round(avg_score * len(scores) / total_ratings, 2)
            }
        
        # Trier par score de préférence
        sorted_prefs = dict(sorted(
            preferences.items(), 
            key=lambda x: x[1]['preference_score'], 
            reverse=True
        ))
        
        return sorted_prefs
    
    def get_recommendations_for_user(self, user_id: str, movie_recommender, 
                                   num_recommendations: int = 10) -> List[Dict]:
        """Génère des recommandations personnalisées pour un utilisateur"""
        preferences = self.get_user_preferences(user_id)
        user_ratings = dict(self.get_user_ratings(user_id))
        
        if not preferences:
            # Utilisateur sans historique - recommandations générales
            return movie_recommender.get_random_movies(num_recommendations)
        
        # Obtenir les genres préférés
        top_genres = list(preferences.keys())[:3]
        
        all_recommendations = []
        
        # Recommandations basées sur les genres préférés
        for genre in top_genres:
            try:
                genre_movies = movie_recommender.search_by_genre(
                    genre, limit=num_recommendations//2
                )
                all_recommendations.extend(genre_movies)
            except:
                continue
        
        # Filtrer les films déjà notés
        filtered_recommendations = [
            movie for movie in all_recommendations 
            if movie['id'] not in user_ratings
        ]
        
        # Scorer selon les préférences
        for movie in filtered_recommendations:
            score = 0
            for genre in movie.get('genres', []):
                if genre in preferences:
                    score += preferences[genre]['preference_score']
            movie['personalized_score'] = score
        
        # Trier par score personnalisé
        filtered_recommendations.sort(
            key=lambda x: x.get('personalized_score', 0), 
            reverse=True
        )
        
        return filtered_recommendations[:num_recommendations]
    
    def get_analytics(self) -> Dict:
        """Génère des analytiques du système"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Statistiques générales
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ratings")
            total_ratings = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(rating) FROM ratings")
            avg_rating = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM recommendation_feedback")
            total_feedback = cursor.fetchone()[0]
            
            # Top genres notés
            cursor.execute('''
                SELECT movie_id, AVG(rating) as avg_rating, COUNT(*) as count
                FROM ratings 
                GROUP BY movie_id 
                ORDER BY avg_rating DESC, count DESC
                LIMIT 10
            ''')
            top_rated_movies = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_users': total_users,
                'total_ratings': total_ratings,
                'average_rating': round(avg_rating, 2),
                'total_feedback': total_feedback,
                'top_rated_movies': top_rated_movies
            }
            
        except Exception as e:
            print(f"❌ Erreur analytics: {e}")
            return {}
    
    def export_user_data(self, user_id: str) -> Dict:
        """Exporte toutes les données d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Notes
            ratings_df = pd.read_sql_query(
                "SELECT * FROM ratings WHERE user_id = ?", 
                conn, params=(user_id,)
            )
            
            # Retours
            feedback_df = pd.read_sql_query(
                "SELECT * FROM recommendation_feedback WHERE user_id = ?", 
                conn, params=(user_id,)
            )
            
            # Interactions
            interactions_df = pd.read_sql_query(
                "SELECT * FROM user_interactions WHERE user_id = ?", 
                conn, params=(user_id,)
            )
            
            conn.close()
            
            return {
                'user_id': user_id,
                'ratings': ratings_df.to_dict('records'),
                'feedback': feedback_df.to_dict('records'),
                'interactions': interactions_df.to_dict('records'),
                'preferences': self.get_user_preferences(user_id)
            }
            
        except Exception as e:
            print(f"❌ Erreur export: {e}")
            return {}

def demo_rating_system():
    """Démonstration du système de notation"""
    print("🎬 Démonstration du Système de Notation")
    print("=======================================")
    
    rating_system = UserRatingSystem()
    
    # Créer des utilisateurs de test
    users = ['alice', 'bob', 'charlie']
    
    # Données de test
    test_ratings = [
        ('alice', 157336, 9.0),  # Interstellar
        ('alice', 335984, 8.5),  # Blade Runner 2049
        ('alice', 244786, 7.0),  # Whiplash
        ('bob', 157336, 7.5),    # Interstellar
        ('bob', 155, 9.0),       # The Dark Knight
        ('bob', 27205, 8.0),     # Inception
        ('charlie', 244786, 9.5), # Whiplash
        ('charlie', 346698, 8.0), # Barbie
        ('charlie', 157336, 6.0), # Interstellar
    ]
    
    # Ajouter les notes
    for user_id, movie_id, rating in test_ratings:
        rating_system.add_rating(user_id, movie_id, rating)
    
    # Afficher les préférences des utilisateurs
    for user_id in users:
        print(f"\n👤 Préférences de {user_id}:")
        preferences = rating_system.get_user_preferences(user_id)
        for genre, data in list(preferences.items())[:3]:
            print(f"  🎭 {genre}: {data['average_rating']}/10 "
                  f"({data['count']} films)")
    
    # Afficher les analytiques
    analytics = rating_system.get_analytics()
    print(f"\n📊 Analytiques du système:")
    print(f"  👥 Utilisateurs: {analytics['total_users']}")
    print(f"  ⭐ Notes totales: {analytics['total_ratings']}")
    print(f"  📈 Note moyenne: {analytics['average_rating']}/10")

if __name__ == "__main__":
    demo_rating_system()
