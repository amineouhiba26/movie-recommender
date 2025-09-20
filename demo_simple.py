#!/usr/bin/env python3
"""
Script de démonstration simple pour les nouvelles fonctionnalités
"""

def demo_expansion():
    """Démonstration simple de l'expansion de données"""
    print("📈 DÉMONSTRATION: Expansion de Base de Données")
    print("-" * 50)
    
    try:
        from data_expander import MovieDataExpander
        
        expander = MovieDataExpander()
        
        # Création d'un échantillon sans API
        print("🎬 Création d'une expansion échantillon...")
        expanded_movies = expander.create_sample_expansion()
        
        print(f"✅ Dataset élargi de {len(expander.current_movies)} à {len(expanded_movies)} films")
        
        # Afficher quelques nouveaux films
        new_movies = expanded_movies[len(expander.current_movies):]
        print("\n🆕 Nouveaux films ajoutés:")
        for movie in new_movies[:3]:
            print(f"  • {movie['title']} ({movie['vote_average']}/10)")
        
        expander.save_expanded_dataset(expanded_movies, 'demo_expanded_dataset.json')
        print("💾 Dataset échantillon sauvegardé: demo_expanded_dataset.json")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🎬 Démonstration du Système Avancé")
    print("=" * 50)
    
    demo_expansion()
    
    print("\n🎯 Pour voir toutes les améliorations:")
    print("python advanced_system.py --demo tout")
