#!/usr/bin/env python3
"""
Script de démarrage pour le système de recommandation avancé
S'assure que tous les composants sont correctement initialisés
"""

import os
import sys
import json
from pathlib import Path
import subprocess

def check_dataset():
    """Vérifie que le dataset de base existe"""
    if not Path('movies_dataset.json').exists():
        print("❌ Dataset manquant: movies_dataset.json")
        return False
    
    try:
        with open('movies_dataset.json', 'r') as f:
            movies = json.load(f)
        print(f"✅ Dataset trouvé: {len(movies)} films")
        return True
    except Exception as e:
        print(f"❌ Erreur lecture dataset: {e}")
        return False

def check_artifacts():
    """Vérifie et crée les artifacts si nécessaire"""
    artifacts_path = Path('artifacts')
    required_files = [
        'similarity_matrix.npy',
        'tfidf_vectorizer.pkl',
        'genre_encoder.pkl',
        'movie_metadata.json'
    ]
    
    missing_files = []
    if not artifacts_path.exists():
        artifacts_path.mkdir()
        missing_files = required_files
    else:
        for file in required_files:
            if not (artifacts_path / file).exists():
                missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Artifacts manquants: {missing_files}")
        print("🔄 Exécution du preprocessing...")
        
        try:
            from preprocess_movies import preprocess_movies
            preprocess_movies(apply_svd=False)
            print("✅ Preprocessing terminé")
            return True
        except Exception as e:
            print(f"❌ Erreur preprocessing: {e}")
            return False
    else:
        print("✅ Tous les artifacts présents")
        return True

def test_components():
    """Test rapide des composants principaux"""
    print("🧪 Test des composants...")
    
    # Test recommandeur de base
    try:
        from movie_recommender import MovieRecommender
        recommender = MovieRecommender()
        test_recs = recommender.recommend_by_title("Interstellar", 3)
        print("✅ Recommandeur de base: OK")
    except Exception as e:
        print(f"❌ Recommandeur de base: {e}")
        return False
    
    # Test système de notation (optionnel)
    try:
        from user_rating_system import UserRatingSystem
        rating_system = UserRatingSystem()
        print("✅ Système de notation: OK")
    except Exception as e:
        print(f"⚠️  Système de notation: {e}")
    
    # Test système hybride (optionnel)
    try:
        from hybrid_recommender import HybridRecommendationSystem
        hybrid_system = HybridRecommendationSystem(recommender, rating_system)
        print("✅ Système hybride: OK")
    except Exception as e:
        print(f"⚠️  Système hybride: {e}")
    
    return True

def create_demo_data():
    """Crée des données de démonstration pour les tests"""
    try:
        from user_rating_system import UserRatingSystem
        rating_system = UserRatingSystem()
        
        # Quelques notes de test
        test_ratings = [
            ('demo_user', 157336, 9.0),   # Interstellar
            ('demo_user', 155, 8.5),      # The Dark Knight
            ('demo_user', 27205, 8.0),    # Inception
        ]
        
        for user_id, movie_id, rating in test_ratings:
            rating_system.add_rating(user_id, movie_id, rating)
        
        print("✅ Données de démonstration créées")
        
    except Exception as e:
        print(f"⚠️  Erreur création données démo: {e}")

def main():
    """Fonction principale de setup"""
    print("🎬 Configuration du Système de Recommandation Avancé")
    print("=" * 55)
    
    # Vérifications
    if not check_dataset():
        print("❌ Dataset requis non trouvé")
        return False
    
    if not check_artifacts():
        print("❌ Problème avec les artifacts")
        return False
    
    if not test_components():
        print("❌ Problème avec les composants")
        return False
    
    # Création des données de démo
    create_demo_data()
    
    print("\n🎉 Système prêt!")
    print("=" * 55)
    print("📝 Pour démarrer l'application:")
    print("   streamlit run streamlit_app.py")
    print("\n🔧 Pour les démos avancées:")
    print("   python advanced_system.py --demo tout")
    print("\n🚀 Pour déployer:")
    print("   - Commitez et pushez vers GitHub")
    print("   - Connectez à Streamlit Cloud")
    print("   - L'app sera automatiquement déployée!")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
