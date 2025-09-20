#!/usr/bin/env python3
"""
Application Streamlit avancée avec toutes les nouvelles fonctionnalités
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
import time
import sqlite3

# Configuration de la page
st.set_page_config(
    page_title="🎬 Recommandations Films Avancées",
    page_icon="🎬",
    layout="wide"
)

@st.cache_data
def load_movies():
    """Charge le dataset de films"""
    try:
        with open('movies_dataset.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Dataset non trouvé. Exécutez d'abord le preprocessing.")
        return []

@st.cache_resource
def initialize_recommender():
    """Initialise le système de recommandation"""
    try:
        # Vérifier si les artifacts existent
        artifacts_path = Path('artifacts')
        if not artifacts_path.exists() or not (artifacts_path / 'similarity_matrix.npy').exists():
            st.info("Configuration initiale du système...")
            with st.spinner("Preprocessing en cours..."):
                from preprocess_movies import preprocess_movies
                preprocess_movies(apply_svd=False)
            st.success("Configuration terminée!")
        
        from movie_recommender import MovieRecommender
        return MovieRecommender()
    except Exception as e:
        st.error(f"Erreur initialisation du recommandeur: {e}")
        return None

@st.cache_resource
def initialize_rating_system():
    """Initialise le système de notation"""
    try:
        from user_rating_system import UserRatingSystem
        return UserRatingSystem()
    except Exception as e:
        st.warning(f"Système de notation non disponible: {e}")
        return None

@st.cache_resource
def initialize_hybrid_system(_content_recommender, _rating_system):
    """Initialise le système hybride"""
    if not _content_recommender or not _rating_system:
        return None
    try:
        from hybrid_recommender import HybridRecommendationSystem
        return HybridRecommendationSystem(_content_recommender, _rating_system)
    except Exception as e:
        st.warning(f"Système hybride non disponible: {e}")
        return None

def display_movie_card(movie, show_score=False):
    """Affiche une carte de film"""
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Placeholder pour l'affiche
            st.image("https://via.placeholder.com/150x225/cccccc/333333?text=🎬", width=100)
        
        with col2:
            st.subheader(movie['title'])
            
            # Genres
            if movie.get('genres'):
                genre_text = " | ".join(movie['genres'])
                st.caption(f"🎭 {genre_text}")
            
            # Note
            if movie.get('vote_average'):
                st.caption(f"⭐ {movie['vote_average']}/10 ({movie.get('vote_count', 0)} votes)")
            
            # Description
            if movie.get('overview'):
                st.write(movie['overview'][:200] + "..." if len(movie['overview']) > 200 else movie['overview'])
            
            # Score de recommandation si disponible
            if show_score and 'hybrid_score' in movie:
                st.metric("Score Hybride", f"{movie['hybrid_score']:.3f}")
                
                with st.expander("Détails du score"):
                    st.write(f"**Contenu**: {movie.get('content_component', 0):.3f}")
                    st.write(f"**Collaboratif**: {movie.get('collaborative_component', 0):.3f}")

def main():
    """Application principale"""
    st.title("🎬 Système de Recommandation de Films Avancé")
    st.markdown("*Découvrez votre prochain film préféré avec l'IA !*")
    
    # Initialisation des composants
    movies = load_movies()
    recommender = initialize_recommender()
    rating_system = initialize_rating_system()
    hybrid_system = initialize_hybrid_system(recommender, rating_system)
    
    if not movies:
        st.stop()
    
    # Sidebar pour la navigation
    st.sidebar.title("🎛️ Navigation")
    page = st.sidebar.selectbox(
        "Choisissez une page",
        ["🔍 Recherche Basique", "⭐ Recommandations Personnalisées", "🎲 Découverte", "📊 Mes Notes", "🔧 Administration"]
    )
    
    # Gestion des utilisateurs
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'user_demo'
    
    user_id = st.sidebar.text_input("👤 ID Utilisateur", value=st.session_state.user_id)
    st.session_state.user_id = user_id
    
    # Page de recherche basique
    if page == "🔍 Recherche Basique":
        st.header("🔍 Recherche de Films Similaires")
        
        # Interface de recherche
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_title = st.text_input("🎬 Titre du film", placeholder="Ex: Interstellar")
        
        with col2:
            num_recs = st.slider("Nombre", 1, 20, 5)
        
        if search_title and recommender:
            try:
                recommendations = recommender.recommend_by_title(search_title, num_recs)
                
                if recommendations:
                    st.success(f"Trouvé {len(recommendations)} recommandations pour '{search_title}'")
                    
                    for i, movie in enumerate(recommendations, 1):
                        st.markdown(f"### {i}. {movie['title']}")
                        display_movie_card(movie)
                        st.divider()
                else:
                    st.warning("Aucune recommandation trouvée")
                    
            except Exception as e:
                st.error(f"Erreur: {e}")
        
        # Recherche par genre
        st.subheader("🎭 Recherche par Genre")
        
        # Extraire tous les genres disponibles
        all_genres = set()
        for movie in movies:
            all_genres.update(movie.get('genres', []))
        
        selected_genre = st.selectbox("Choisissez un genre", sorted(all_genres))
        
        if selected_genre and recommender:
            try:
                genre_movies = recommender.search_by_genre(selected_genre, limit=num_recs)
                
                if genre_movies:
                    st.success(f"Trouvé {len(genre_movies)} films {selected_genre}")
                    
                    for movie in genre_movies:
                        display_movie_card(movie)
                        st.divider()
                        
            except Exception as e:
                st.error(f"Erreur recherche par genre: {e}")
    
    # Page de recommandations personnalisées
    elif page == "⭐ Recommandations Personnalisées":
        st.header("⭐ Recommandations Personnalisées")
        
        if not hybrid_system:
            st.warning("Système hybride non disponible. Utilisation du système de base.")
            
            if recommender:
                # Recommandations aléatoires comme fallback
                st.subheader("🎲 Suggestions Aléatoires")
                random_movies = recommender.get_random_movies(10)
                
                for movie in random_movies:
                    display_movie_card(movie)
                    st.divider()
        else:
            # Afficher les préférences utilisateur
            if rating_system:
                user_prefs = rating_system.get_user_preferences(user_id)
                
                if user_prefs:
                    st.subheader("🎯 Vos Préférences")
                    
                    pref_df = pd.DataFrame([
                        {
                            'Genre': genre,
                            'Note Moyenne': data['average_rating'],
                            'Nombre de Films': data['count'],
                            'Score de Préférence': data['preference_score']
                        }
                        for genre, data in list(user_prefs.items())[:5]
                    ])
                    
                    st.dataframe(pref_df, use_container_width=True)
                
                # Recommandations hybrides
                st.subheader("🔀 Recommandations Hybrides")
                
                num_hybrid_recs = st.slider("Nombre de recommandations", 1, 20, 8)
                
                try:
                    hybrid_recs = hybrid_system.get_hybrid_recommendations(
                        user_id, 
                        num_recommendations=num_hybrid_recs
                    )
                    
                    if hybrid_recs:
                        st.success(f"Recommandations personnalisées pour {user_id}")
                        
                        for i, movie in enumerate(hybrid_recs, 1):
                            st.markdown(f"### {i}. Recommandation Hybride")
                            display_movie_card(movie, show_score=True)
                            st.divider()
                    else:
                        st.info("Pas encore assez de données pour des recommandations personnalisées. Notez quelques films d'abord!")
                        
                except Exception as e:
                    st.error(f"Erreur recommandations hybrides: {e}")
    
    # Page de découverte
    elif page == "🎲 Découverte":
        st.header("🎲 Découverte de Films")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎲 Films Aléatoires", use_container_width=True):
                if recommender:
                    random_movies = recommender.get_random_movies(6)
                    
                    st.subheader("Films à Découvrir")
                    for movie in random_movies:
                        display_movie_card(movie)
                        st.divider()
        
        with col2:
            if st.button("🏆 Mieux Notés", use_container_width=True):
                # Trier par note
                sorted_movies = sorted(movies, key=lambda x: x.get('vote_average', 0), reverse=True)
                
                st.subheader("Films les Mieux Notés")
                for movie in sorted_movies[:6]:
                    display_movie_card(movie)
                    st.divider()
    
    # Page de notation
    elif page == "📊 Mes Notes":
        st.header("📊 Mes Notes et Préférences")
        
        if not rating_system:
            st.warning("Système de notation non disponible")
            return
        
        # Interface de notation
        st.subheader("⭐ Noter un Film")
        
        # Sélection de film
        movie_titles = {movie['title']: movie['id'] for movie in movies}
        selected_title = st.selectbox("Choisir un film à noter", list(movie_titles.keys()))
        
        if selected_title:
            movie_id = movie_titles[selected_title]
            
            # Interface de notation
            col1, col2 = st.columns([2, 1])
            
            with col1:
                rating = st.slider("Note (0-10)", 0.0, 10.0, 5.0, 0.5)
            
            with col2:
                if st.button("💾 Sauvegarder Note"):
                    if rating_system.add_rating(user_id, movie_id, rating):
                        st.success(f"Note {rating}/10 sauvegardée pour '{selected_title}'")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la sauvegarde")
        
        # Afficher les notes existantes
        user_ratings = rating_system.get_user_ratings(user_id)
        
        if user_ratings:
            st.subheader("📝 Vos Notes")
            
            # Créer un DataFrame des notes
            ratings_data = []
            movies_dict = {movie['id']: movie for movie in movies}
            
            for movie_id, rating in user_ratings:
                if movie_id in movies_dict:
                    movie = movies_dict[movie_id]
                    ratings_data.append({
                        'Film': movie['title'],
                        'Ma Note': f"{rating}/10",
                        'Note TMDB': f"{movie.get('vote_average', 'N/A')}/10",
                        'Genres': ' | '.join(movie.get('genres', []))
                    })
            
            if ratings_data:
                ratings_df = pd.DataFrame(ratings_data)
                st.dataframe(ratings_df, use_container_width=True)
        else:
            st.info("Aucune note enregistrée. Commencez par noter quelques films!")
    
    # Page d'administration
    elif page == "🔧 Administration":
        st.header("🔧 Administration du Système")
        
        # Statistiques du dataset
        st.subheader("📊 Statistiques du Dataset")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Films Totaux", len(movies))
        
        with col2:
            all_genres = set()
            for movie in movies:
                all_genres.update(movie.get('genres', []))
            st.metric("Genres", len(all_genres))
        
        with col3:
            avg_rating = np.mean([movie.get('vote_average', 0) for movie in movies])
            st.metric("Note Moyenne", f"{avg_rating:.1f}/10")
        
        with col4:
            # Statistiques utilisateur si disponible
            if rating_system:
                try:
                    analytics = rating_system.get_analytics()
                    st.metric("Utilisateurs", analytics.get('total_users', 0))
                except:
                    st.metric("Utilisateurs", "N/A")
        
        # Expansion du dataset
        st.subheader("📈 Expansion du Dataset")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Créer Échantillon Élargi"):
                try:
                    from data_expander import MovieDataExpander
                    
                    with st.spinner("Création de l'échantillon..."):
                        expander = MovieDataExpander()
                        expanded_movies = expander.create_sample_expansion()
                        expander.save_expanded_dataset(expanded_movies, 'movies_dataset_expanded.json')
                    
                    st.success(f"Dataset élargi créé! {len(expanded_movies)} films")
                    
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        with col2:
            api_key = st.text_input("🔑 Clé API TMDB (optionnelle)", type="password")
            target_size = st.number_input("Taille cible", 100, 2000, 500)
            
            if st.button("🚀 Expansion Complète") and api_key:
                try:
                    from data_expander import MovieDataExpander
                    
                    with st.spinner(f"Expansion vers {target_size} films..."):
                        expander = MovieDataExpander(api_key)
                        expanded_movies = expander.expand_dataset(target_size)
                        expander.save_expanded_dataset(expanded_movies)
                    
                    st.success(f"Dataset élargi! {len(expanded_movies)} films")
                    
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        # Test des composants
        st.subheader("🧪 Tests des Composants")
        
        if st.button("🔬 Test Complet du Système"):
            with st.spinner("Exécution des tests..."):
                results = []
                
                # Test recommandeur de base
                try:
                    test_recs = recommender.recommend_by_title("Interstellar", 3)
                    results.append("✅ Recommandeur de base: OK")
                except Exception as e:
                    results.append(f"❌ Recommandeur de base: {e}")
                
                # Test système de notation
                try:
                    rating_system.add_rating('test_user', 157336, 8.0)
                    results.append("✅ Système de notation: OK")
                except Exception as e:
                    results.append(f"❌ Système de notation: {e}")
                
                # Test système hybride
                if hybrid_system:
                    try:
                        hybrid_recs = hybrid_system.get_hybrid_recommendations('test_user', 3)
                        results.append("✅ Système hybride: OK")
                    except Exception as e:
                        results.append(f"❌ Système hybride: {e}")
                else:
                    results.append("⚠️ Système hybride: Non disponible")
                
                # Afficher les résultats
                for result in results:
                    if "✅" in result:
                        st.success(result)
                    elif "❌" in result:
                        st.error(result)
                    else:
                        st.warning(result)

if __name__ == "__main__":
    main()
