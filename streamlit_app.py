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
    page_title="Système de Recommandation de Films",
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
        st.subheader(movie['title'])
        
        # Genres
        if movie.get('genres'):
            genre_text = " | ".join(movie['genres'])
            st.caption(f"Genres: {genre_text}")
        
        # Note
        if movie.get('vote_average'):
            st.caption(f"Note: {movie['vote_average']}/10 ({movie.get('vote_count', 0)} votes)")
        
        # Description
        if movie.get('overview'):
            st.write(movie['overview'][:200] + "..." if len(movie['overview']) > 200 else movie['overview'])
        
        # Score de recommandation si disponible
        if show_score and 'hybrid_score' in movie:
            st.metric("Score de Recommandation", f"{movie['hybrid_score']:.3f}")
            
            with st.expander("Détails du score"):
                st.write(f"**Contenu**: {movie.get('content_component', 0):.3f}")
                st.write(f"**Collaboratif**: {movie.get('collaborative_component', 0):.3f}")

def main():
    """Application principale"""
    st.title("Système de Recommandation de Films")
    st.markdown("*Découvrez votre prochain film préféré avec l'IA*")
    
    # Initialisation des composants
    movies = load_movies()
    recommender = initialize_recommender()
    rating_system = initialize_rating_system()
    hybrid_system = initialize_hybrid_system(recommender, rating_system)
    
    if not movies:
        st.stop()
    
    # Sidebar pour la navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choisissez une page",
        ["Recherche", "Recommandations Hybrides", "Mes Notes"]
    )
    
    # Gestion des utilisateurs
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'user_demo'
    
    user_id = st.sidebar.text_input("ID Utilisateur", value=st.session_state.user_id)
    st.session_state.user_id = user_id
    
    # Page de recherche basique
    if page == "Recherche":
        st.header("Recherche de Films Similaires")
        
        # Interface de recherche
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_title = st.text_input("Titre du film", placeholder="Ex: Interstellar")
        
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
        st.subheader("Recherche par Genre")
        
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
    
    # Page de recommandations hybrides
    elif page == "Recommandations Hybrides":
        st.header("Recommandations Hybrides")
        
        if not hybrid_system:
            st.warning("Système hybride non disponible. Veuillez noter quelques films d'abord.")
            return
        
        # Afficher les préférences utilisateur
        if rating_system:
            user_prefs = rating_system.get_user_preferences(user_id)
            
            if user_prefs:
                st.subheader("Vos Préférences")
                
                pref_df = pd.DataFrame([
                    {
                        'Genre': genre,
                        'Note Moyenne': data['average_rating'],
                        'Nombre de Films': data['count'],
                        'Score de Préférence': data['preference_score']
                    }
                    for genre, data in list(user_prefs.items())[:5]
                ])
                
                st.dataframe(pref_df, width="stretch")
            
            # Recommandations hybrides
            st.subheader("Recommandations Personnalisées")
            st.caption("Combinaison de filtrage par contenu et collaboratif")
            
            num_hybrid_recs = st.slider("Nombre de recommandations", 1, 20, 8)
            
            try:
                hybrid_recs = hybrid_system.get_hybrid_recommendations(
                    user_id, 
                    num_recommendations=num_hybrid_recs
                )
                
                if hybrid_recs:
                    st.success(f"Recommandations personnalisées pour {user_id}")
                    
                    for i, movie in enumerate(hybrid_recs, 1):
                        st.markdown(f"### {i}. Recommandation")
                        display_movie_card(movie, show_score=True)
                        st.divider()
                else:
                    st.info("Pas encore assez de données pour des recommandations personnalisées. Notez quelques films d'abord!")
                    
            except Exception as e:
                st.error(f"Erreur recommandations hybrides: {e}")
    
    # Page de notation
    elif page == "Mes Notes":
        st.header("Mes Notes et Préférences")
        
        if not rating_system:
            st.warning("Système de notation non disponible")
            return
        
        # Interface de notation
        st.subheader("Noter un Film")
        
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
                if st.button("Sauvegarder Note"):
                    if rating_system.add_rating(user_id, movie_id, rating):
                        st.success(f"Note {rating}/10 sauvegardée pour '{selected_title}'")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la sauvegarde")
        
        # Afficher les notes existantes
        user_ratings = rating_system.get_user_ratings(user_id)
        
        if user_ratings:
            st.subheader("Vos Notes")
            
            # Créer un DataFrame des notes avec option de suppression
            movies_dict = {movie['id']: movie for movie in movies}
            
            for movie_id, rating in user_ratings:
                if movie_id in movies_dict:
                    movie = movies_dict[movie_id]
                    
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(f"**{movie['title']}** - {rating}/10")
                        st.caption(f"Note TMDB: {movie.get('vote_average', 'N/A')}/10 | Genres: {' | '.join(movie.get('genres', []))}")
                    
                    with col2:
                        if st.button("Supprimer", key=f"delete_{movie_id}"):
                            if rating_system.delete_rating(user_id, movie_id):
                                st.success("Note supprimée!")
                                st.rerun()
                            else:
                                st.error("Erreur lors de la suppression")
                    
                    st.divider()
        else:
            st.info("Aucune note enregistrée. Commencez par noter quelques films!")

if __name__ == "__main__":
    main()
