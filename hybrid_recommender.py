#!/usr/bin/env python3
"""
Système de filtrage hybride
Combine le filtrage basé sur le contenu avec le filtrage collaboratif
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import json
import sqlite3
from typing import Dict, List, Tuple, Optional
import pickle
from pathlib import Path

class HybridRecommendationSystem:
    """Système de recommandation hybride"""
    
    def __init__(self, content_recommender, rating_system, 
                 content_weight: float = 0.7, collaborative_weight: float = 0.3):
        self.content_recommender = content_recommender
        self.rating_system = rating_system
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight
        
        # Modèles collaboratifs
        self.user_movie_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.svd_model = None
        self.user_factors = None
        self.item_factors = None
        
        self.is_trained = False
        
    def build_user_movie_matrix(self) -> csr_matrix:
        """Construit la matrice utilisateur-film à partir des notes"""
        try:
            conn = sqlite3.connect(self.rating_system.db_path)
            ratings_df = pd.read_sql_query(
                "SELECT user_id, movie_id, rating FROM ratings", conn
            )
            conn.close()
            
            if ratings_df.empty:
                print("⚠️  Aucune note trouvée, filtrage collaboratif désactivé")
                return None
            
            # Créer la matrice pivot
            user_movie_matrix = ratings_df.pivot(
                index='user_id', 
                columns='movie_id', 
                values='rating'
            ).fillna(0)
            
            print(f"📊 Matrice utilisateur-film: {user_movie_matrix.shape}")
            
            # Convertir en matrice sparse pour l'efficacité
            sparse_matrix = csr_matrix(user_movie_matrix.values)
            
            self.user_movie_matrix = user_movie_matrix
            return sparse_matrix
            
        except Exception as e:
            print(f"❌ Erreur construction matrice: {e}")
            return None
    
    def train_collaborative_models(self):
        """Entraîne les modèles de filtrage collaboratif"""
        print("🤖 Entraînement des modèles collaboratifs...")
        
        sparse_matrix = self.build_user_movie_matrix()
        if sparse_matrix is None:
            return
        
        # 1. Similarité utilisateur-utilisateur
        try:
            user_similarity = cosine_similarity(sparse_matrix)
            self.user_similarity_matrix = user_similarity
            print("✅ Similarité utilisateur calculée")
        except Exception as e:
            print(f"❌ Erreur similarité utilisateur: {e}")
        
        # 2. Similarité item-item
        try:
            item_similarity = cosine_similarity(sparse_matrix.T)
            self.item_similarity_matrix = item_similarity
            print("✅ Similarité item calculée")
        except Exception as e:
            print(f"❌ Erreur similarité item: {e}")
        
        # 3. Factorisation matricielle (SVD)
        try:
            n_components = min(50, min(sparse_matrix.shape) - 1)
            self.svd_model = TruncatedSVD(
                n_components=n_components, 
                random_state=42
            )
            
            # Entraîner SVD
            user_factors = self.svd_model.fit_transform(sparse_matrix)
            item_factors = self.svd_model.components_.T
            
            self.user_factors = user_factors
            self.item_factors = item_factors
            
            print(f"✅ SVD entraîné ({n_components} facteurs)")
        except Exception as e:
            print(f"❌ Erreur SVD: {e}")
        
        self.is_trained = True
        print("🎯 Modèles collaboratifs prêts")
    
    def get_collaborative_recommendations(self, user_id: str, 
                                        num_recommendations: int = 10) -> List[Dict]:
        """Génère des recommandations collaboratives pour un utilisateur"""
        if not self.is_trained:
            self.train_collaborative_models()
        
        if self.user_movie_matrix is None:
            return []
        
        try:
            if user_id not in self.user_movie_matrix.index:
                return []
            
            user_idx = self.user_movie_matrix.index.get_loc(user_id)
            user_ratings = self.user_movie_matrix.iloc[user_idx]
            
            # Méthode 1: Similarité utilisateur-utilisateur
            user_based_scores = self._get_user_based_scores(user_idx, user_ratings)
            
            # Méthode 2: Factorisation matricielle
            matrix_factorization_scores = self._get_matrix_factorization_scores(user_idx)
            
            # Combiner les scores collaboratifs
            combined_scores = {}
            all_movie_ids = set(user_based_scores.keys()) | set(matrix_factorization_scores.keys())
            
            for movie_id in all_movie_ids:
                score = 0
                count = 0
                
                if movie_id in user_based_scores:
                    score += user_based_scores[movie_id]
                    count += 1
                
                if movie_id in matrix_factorization_scores:
                    score += matrix_factorization_scores[movie_id]
                    count += 1
                
                if count > 0:
                    combined_scores[movie_id] = score / count
            
            # Trier et formater les recommandations
            sorted_recommendations = sorted(
                combined_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:num_recommendations]
            
            # Convertir en format standard
            recommendations = []
            movies_dict = self._load_movies_dict()
            
            for movie_id, score in sorted_recommendations:
                if movie_id in movies_dict:
                    movie = movies_dict[movie_id].copy()
                    movie['collaborative_score'] = round(score, 3)
                    recommendations.append(movie)
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Erreur recommandations collaboratives: {e}")
            return []
    
    def _get_user_based_scores(self, user_idx: int, user_ratings: pd.Series) -> Dict[int, float]:
        """Calcule les scores basés sur la similarité utilisateur"""
        if self.user_similarity_matrix is None:
            return {}
        
        scores = {}
        user_similarities = self.user_similarity_matrix[user_idx]
        
        # Trouver les utilisateurs similaires
        similar_users = np.argsort(user_similarities)[::-1][1:11]  # Top 10 sans soi-même
        
        for similar_user_idx in similar_users:
            similarity = user_similarities[similar_user_idx]
            if similarity > 0.1:  # Seuil de similarité
                similar_user_ratings = self.user_movie_matrix.iloc[similar_user_idx]
                
                for movie_id, rating in similar_user_ratings.items():
                    if rating > 0 and user_ratings[movie_id] == 0:  # Film non vu par l'utilisateur
                        if movie_id not in scores:
                            scores[movie_id] = 0
                        scores[movie_id] += similarity * rating
        
        return scores
    
    def _get_matrix_factorization_scores(self, user_idx: int) -> Dict[int, float]:
        """Calcule les scores basés sur la factorisation matricielle"""
        if self.user_factors is None or self.item_factors is None:
            return {}
        
        scores = {}
        user_vector = self.user_factors[user_idx]
        
        # Calculer les scores prédits pour tous les films
        predicted_ratings = np.dot(user_vector, self.item_factors.T)
        
        movie_ids = self.user_movie_matrix.columns
        user_ratings = self.user_movie_matrix.iloc[user_idx]
        
        for i, movie_id in enumerate(movie_ids):
            if user_ratings[movie_id] == 0:  # Film non vu
                scores[movie_id] = predicted_ratings[i]
        
        return scores
    
    def get_hybrid_recommendations(self, user_id: str, movie_title: Optional[str] = None,
                                 num_recommendations: int = 10) -> List[Dict]:
        """Génère des recommandations hybrides"""
        print(f"🔀 Génération de recommandations hybrides pour {user_id}")
        
        # Recommandations basées sur le contenu
        if movie_title:
            content_recommendations = self.content_recommender.recommend_by_title(
                movie_title, num_recommendations * 2
            )
        else:
            # Utiliser les préférences utilisateur pour le contenu
            user_preferences = self.rating_system.get_user_preferences(user_id)
            if user_preferences:
                top_genre = list(user_preferences.keys())[0]
                content_recommendations = self.content_recommender.search_by_genre(
                    top_genre, num_recommendations * 2
                )
            else:
                content_recommendations = self.content_recommender.get_random_movies(
                    num_recommendations * 2
                )
        
        # Recommandations collaboratives
        collaborative_recommendations = self.get_collaborative_recommendations(
            user_id, num_recommendations * 2
        )
        
        # Combiner les recommandations
        hybrid_scores = {}
        
        # Scorer les recommandations de contenu
        for i, movie in enumerate(content_recommendations):
            movie_id = movie['id']
            # Score basé sur la position (plus haut = meilleur)
            content_score = (len(content_recommendations) - i) / len(content_recommendations)
            hybrid_scores[movie_id] = {
                'movie': movie,
                'content_score': content_score,
                'collaborative_score': 0
            }
        
        # Ajouter les scores collaboratifs
        for i, movie in enumerate(collaborative_recommendations):
            movie_id = movie['id']
            collab_score = (len(collaborative_recommendations) - i) / len(collaborative_recommendations)
            
            if movie_id in hybrid_scores:
                hybrid_scores[movie_id]['collaborative_score'] = collab_score
            else:
                hybrid_scores[movie_id] = {
                    'movie': movie,
                    'content_score': 0,
                    'collaborative_score': collab_score
                }
        
        # Calculer le score hybride final
        final_recommendations = []
        for movie_id, scores in hybrid_scores.items():
            movie = scores['movie']
            
            # Score hybride pondéré
            hybrid_score = (
                self.content_weight * scores['content_score'] +
                self.collaborative_weight * scores['collaborative_score']
            )
            
            movie['hybrid_score'] = round(hybrid_score, 3)
            movie['content_component'] = round(scores['content_score'], 3)
            movie['collaborative_component'] = round(scores['collaborative_score'], 3)
            
            final_recommendations.append(movie)
        
        # Trier par score hybride
        final_recommendations.sort(
            key=lambda x: x['hybrid_score'], 
            reverse=True
        )
        
        # Filtrer les films déjà notés par l'utilisateur
        user_ratings = dict(self.rating_system.get_user_ratings(user_id))
        filtered_recommendations = [
            movie for movie in final_recommendations 
            if movie['id'] not in user_ratings
        ]
        
        return filtered_recommendations[:num_recommendations]
    
    def _load_movies_dict(self) -> Dict[int, Dict]:
        """Charge le dictionnaire des films"""
        try:
            with open('movies_dataset.json', 'r', encoding='utf-8') as f:
                movies = json.load(f)
            return {movie['id']: movie for movie in movies}
        except:
            return {}
    
    def evaluate_recommendations(self, test_user_id: str, held_out_movies: List[int]) -> Dict:
        """Évalue la qualité des recommandations"""
        recommendations = self.get_hybrid_recommendations(test_user_id, num_recommendations=20)
        recommended_ids = [movie['id'] for movie in recommendations]
        
        # Calculer les métriques
        hits = len(set(recommended_ids) & set(held_out_movies))
        precision = hits / len(recommended_ids) if recommended_ids else 0
        recall = hits / len(held_out_movies) if held_out_movies else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1_score': round(f1, 3),
            'hits': hits,
            'total_recommendations': len(recommended_ids),
            'total_held_out': len(held_out_movies)
        }
    
    def save_models(self, filepath: str = 'hybrid_models.pkl'):
        """Sauvegarde les modèles entraînés"""
        try:
            models = {
                'user_similarity_matrix': self.user_similarity_matrix,
                'item_similarity_matrix': self.item_similarity_matrix,
                'svd_model': self.svd_model,
                'user_factors': self.user_factors,
                'item_factors': self.item_factors,
                'user_movie_matrix': self.user_movie_matrix,
                'content_weight': self.content_weight,
                'collaborative_weight': self.collaborative_weight,
                'is_trained': self.is_trained
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(models, f)
            
            print(f"💾 Modèles sauvegardés: {filepath}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def load_models(self, filepath: str = 'hybrid_models.pkl'):
        """Charge les modèles sauvegardés"""
        try:
            with open(filepath, 'rb') as f:
                models = pickle.load(f)
            
            self.user_similarity_matrix = models.get('user_similarity_matrix')
            self.item_similarity_matrix = models.get('item_similarity_matrix')
            self.svd_model = models.get('svd_model')
            self.user_factors = models.get('user_factors')
            self.item_factors = models.get('item_factors')
            self.user_movie_matrix = models.get('user_movie_matrix')
            self.content_weight = models.get('content_weight', 0.7)
            self.collaborative_weight = models.get('collaborative_weight', 0.3)
            self.is_trained = models.get('is_trained', False)
            
            print(f"📥 Modèles chargés: {filepath}")
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")

def demo_hybrid_system():
    """Démonstration du système hybride"""
    print("🔀 Démonstration du Système Hybride")
    print("===================================")
    
    # Initialiser les composants (simulation)
    from movie_recommender import MovieRecommender
    from user_rating_system import UserRatingSystem
    
    try:
        content_recommender = MovieRecommender()
        rating_system = UserRatingSystem()
        
        # Créer le système hybride
        hybrid_system = HybridRecommendationSystem(
            content_recommender, 
            rating_system,
            content_weight=0.6,
            collaborative_weight=0.4
        )
        
        # Entraîner les modèles
        hybrid_system.train_collaborative_models()
        
        # Test avec un utilisateur
        test_user = 'alice'
        recommendations = hybrid_system.get_hybrid_recommendations(
            test_user, 
            num_recommendations=5
        )
        
        print(f"\n🎬 Recommandations hybrides pour {test_user}:")
        for i, movie in enumerate(recommendations, 1):
            print(f"{i}. {movie['title']}")
            print(f"   Score hybride: {movie['hybrid_score']}")
            print(f"   Contenu: {movie['content_component']} | "
                  f"Collaboratif: {movie['collaborative_component']}")
            print()
        
    except Exception as e:
        print(f"❌ Erreur démonstration: {e}")
        print("💡 Assurez-vous que movie_recommender.py et user_rating_system.py existent")

if __name__ == "__main__":
    demo_hybrid_system()
