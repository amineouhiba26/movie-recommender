#!/usr/bin/env python3
"""
Système de recommandation de films avancé
Intègre tous les composants améliorés
"""

import json
import argparse
from pathlib import Path
import time

def main():
    """Interface principale pour les améliorations"""
    parser = argparse.ArgumentParser(description="Système de Recommandation de Films Avancé")
    parser.add_argument('--demo', choices=['expansion', 'notation', 'hybride', 'temps-reel', 'tout'], 
                       help='Lancer une démonstration')
    parser.add_argument('--expand', action='store_true', help='Élargir la base de données')
    parser.add_argument('--api-key', type=str, help='Clé API TMDB pour l\'expansion')
    parser.add_argument('--target-size', type=int, default=500, 
                       help='Taille cible pour l\'expansion (défaut: 500)')
    
    args = parser.parse_args()
    
    print("🎬 Système de Recommandation de Films Avancé")
    print("=" * 50)
    
    if args.demo:
        run_demos(args.demo)
    elif args.expand:
        expand_database(args.api_key, args.target_size)
    else:
        show_menu()

def show_menu():
    """Affiche le menu principal"""
    print("""
Améliorations disponibles:

1. 📈 Élargissement de la base de données
   - Ajouter des milliers de films depuis TMDB
   - Diversifier les genres et époques
   
2. ⭐ Système de notation utilisateur
   - Permettre aux utilisateurs de noter les films
   - Analyser les préférences individuelles
   
3. 🔀 Filtrage hybride
   - Combiner recommandations de contenu et collaboratives
   - Améliorer la précision des suggestions
   
4. ⚡ Mises à jour temps réel
   - Adapter les modèles automatiquement
   - Apprentissage continu des préférences

Utilisation:
  python advanced_system.py --demo tout              # Toutes les démos
  python advanced_system.py --demo expansion         # Démo expansion
  python advanced_system.py --expand --api-key XXX   # Élargir la DB
""")

def run_demos(demo_type):
    """Lance les démonstrations"""
    print(f"🎭 Lancement de la démonstration: {demo_type}")
    
    if demo_type == 'expansion' or demo_type == 'tout':
        print("\n" + "="*50)
        print("📈 DÉMONSTRATION: Élargissement de la base de données")
        print("="*50)
        
        try:
            from data_expander import demo_expansion
            demo_expansion()
        except ImportError:
            print("❌ Module data_expander non trouvé")
        except Exception as e:
            print(f"❌ Erreur démonstration expansion: {e}")
    
    if demo_type == 'notation' or demo_type == 'tout':
        print("\n" + "="*50)
        print("⭐ DÉMONSTRATION: Système de notation")
        print("="*50)
        
        try:
            from user_rating_system import demo_rating_system
            demo_rating_system()
        except ImportError:
            print("❌ Module user_rating_system non trouvé")
        except Exception as e:
            print(f"❌ Erreur démonstration notation: {e}")
    
    if demo_type == 'hybride' or demo_type == 'tout':
        print("\n" + "="*50)
        print("🔀 DÉMONSTRATION: Système hybride")
        print("="*50)
        
        try:
            from hybrid_recommender import demo_hybrid_system
            demo_hybrid_system()
        except ImportError:
            print("❌ Module hybrid_recommender non trouvé")
        except Exception as e:
            print(f"❌ Erreur démonstration hybride: {e}")
    
    if demo_type == 'temps-reel' or demo_type == 'tout':
        print("\n" + "="*50)
        print("⚡ DÉMONSTRATION: Système temps réel")
        print("="*50)
        
        try:
            from realtime_updater import demo_realtime_system
            demo_realtime_system()
        except ImportError:
            print("❌ Module realtime_updater non trouvé")
        except Exception as e:
            print(f"❌ Erreur démonstration temps réel: {e}")

def expand_database(api_key, target_size):
    """Élargit la base de données"""
    print(f"📈 Élargissement de la base de données vers {target_size} films...")
    
    try:
        from data_expander import MovieDataExpander
        
        expander = MovieDataExpander(api_key)
        
        if api_key:
            expanded_movies = expander.expand_dataset(target_size)
            expander.save_expanded_dataset(expanded_movies)
            print(f"✅ Base de données élargie à {len(expanded_movies)} films")
        else:
            print("⚠️  Aucune clé API fournie, création d'un échantillon...")
            sample_movies = expander.create_sample_expansion()
            expander.save_expanded_dataset(sample_movies, 'movies_dataset_sample.json')
            print(f"✅ Échantillon créé avec {len(sample_movies)} films")
    
    except ImportError:
        print("❌ Module data_expander non trouvé")
    except Exception as e:
        print(f"❌ Erreur lors de l'expansion: {e}")

def setup_advanced_system():
    """Configure le système avancé complet"""
    print("🔧 Configuration du système avancé...")
    
    # Créer les dossiers nécessaires
    Path('models').mkdir(exist_ok=True)
    Path('models/backups').mkdir(exist_ok=True)
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    print("✅ Dossiers créés")
    
    # Vérifier les dépendances
    required_modules = [
        'movie_recommender',
        'user_rating_system', 
        'hybrid_recommender',
        'realtime_updater',
        'data_expander'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"⚠️  Modules manquants: {missing_modules}")
    else:
        print("✅ Tous les modules sont disponibles")
    
    return len(missing_modules) == 0

def create_demo_data():
    """Crée des données de démonstration"""
    print("🎭 Création de données de démonstration...")
    
    try:
        from user_rating_system import UserRatingSystem
        
        rating_system = UserRatingSystem()
        
        # Créer des utilisateurs et notes de test
        demo_users = ['alice', 'bob', 'charlie', 'diana']
        demo_ratings = [
            ('alice', 157336, 9.0),   # Interstellar
            ('alice', 335984, 8.5),   # Blade Runner 2049
            ('alice', 244786, 7.0),   # Whiplash
            ('bob', 157336, 7.5),     # Interstellar
            ('bob', 155, 9.0),        # The Dark Knight
            ('bob', 27205, 8.0),      # Inception
            ('charlie', 244786, 9.5), # Whiplash
            ('charlie', 346698, 8.0), # Barbie
            ('charlie', 157336, 6.0), # Interstellar
            ('diana', 155, 8.8),      # The Dark Knight
            ('diana', 27205, 9.2),    # Inception
            ('diana', 335984, 8.0),   # Blade Runner 2049
        ]
        
        for user_id, movie_id, rating in demo_ratings:
            rating_system.add_rating(user_id, movie_id, rating)
        
        print(f"✅ {len(demo_ratings)} notes de démonstration créées")
        print(f"👥 {len(demo_users)} utilisateurs de test")
        
    except Exception as e:
        print(f"❌ Erreur création données démo: {e}")

def run_integration_test():
    """Lance un test d'intégration complet"""
    print("🧪 Test d'intégration du système avancé")
    print("=" * 40)
    
    try:
        # 1. Système de base
        print("1️⃣  Test du système de base...")
        from movie_recommender import MovieRecommender
        recommender = MovieRecommender()
        basic_recs = recommender.recommend_by_title("Interstellar", 3)
        print(f"   ✅ {len(basic_recs)} recommandations de base")
        
        # 2. Système de notation
        print("2️⃣  Test du système de notation...")
        from user_rating_system import UserRatingSystem
        rating_system = UserRatingSystem()
        rating_system.add_rating('test_user', 157336, 8.5)
        user_prefs = rating_system.get_user_preferences('test_user')
        print(f"   ✅ Préférences utilisateur calculées")
        
        # 3. Système hybride
        print("3️⃣  Test du système hybride...")
        from hybrid_recommender import HybridRecommendationSystem
        hybrid_system = HybridRecommendationSystem(recommender, rating_system)
        hybrid_recs = hybrid_system.get_hybrid_recommendations('test_user', num_recommendations=3)
        print(f"   ✅ {len(hybrid_recs)} recommandations hybrides")
        
        # 4. Système temps réel
        print("4️⃣  Test du système temps réel...")
        from realtime_updater import RealTimeModelUpdater
        updater = RealTimeModelUpdater(hybrid_system, rating_system, update_interval=5)
        status = updater.get_system_status()
        print(f"   ✅ Système temps réel initialisé")
        
        print("\n🎉 Tous les tests d'intégration réussis!")
        return True
        
    except Exception as e:
        print(f"❌ Échec du test d'intégration: {e}")
        return False

if __name__ == "__main__":
    # Configuration initiale
    if setup_advanced_system():
        main()
    else:
        print("❌ Configuration incomplète. Vérifiez les modules manquants.")
