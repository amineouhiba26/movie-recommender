import streamlit as st
import pandas as pd
from movie_recommender import MovieRecommender
import json

# Page config
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'recommender' not in st.session_state:
    try:
        # Check if artifacts exist, if not run preprocessing
        import os
        if not os.path.exists("artifacts/similarity_matrix.npy"):
            st.info("Setting up the recommendation system for first time use...")
            with st.spinner("Running preprocessing... This may take a few minutes."):
                from preprocess_movies import preprocess_movies
                preprocess_movies(apply_svd=False)
            st.success("Setup complete!")
        
        st.session_state.recommender = MovieRecommender()
    except FileNotFoundError:
        st.error("Movie dataset not found. Please ensure movies_dataset.json exists.")
        st.stop()
    except Exception as e:
        st.error(f"Error initializing recommender: {e}")
        st.stop()

recommender = st.session_state.recommender

# Title and description
st.title("🎬 Movie Recommendation System")
st.markdown("Find your next favorite movie based on what you already love!")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Search by Title", "Browse by Genre", "Random Discovery", "Dataset Stats"]
)

if page == "Search by Title":
    st.header("🔍 Search by Movie Title")
    
    # Search input
    title_query = st.text_input("Enter a movie title:", placeholder="e.g., Interstellar, The Matrix")
    num_recs = st.slider("Number of recommendations:", min_value=1, max_value=20, value=10)
    
    if st.button("Get Recommendations") and title_query:
        with st.spinner("Finding recommendations..."):
            result = recommender.recommend_by_title(title_query, num_recs)
            
            if "error" in result:
                st.error(result["error"])
            else:
                # Show matched movie
                matched = result["matched_movie"]
                st.success(f"Found: **{matched['title']}**")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Genres:** {', '.join(matched['genres'])}")
                    st.write(f"**Overview:** {matched['overview']}")
                
                with col2:
                    st.metric("Rating", f"{matched['vote_average']}/10")
                    st.metric("Votes", matched['vote_count'])
                
                # Show other matches if any
                if result["other_matches"]:
                    with st.expander("Other possible matches"):
                        for match in result["other_matches"]:
                            st.write(f"- {match['title']} (Score: {match['score']:.2f})")
                
                # Show recommendations
                st.subheader(f"🎯 Top {len(result['recommendations'])} Recommendations")
                
                for i, rec in enumerate(result["recommendations"], 1):
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{i}. {rec['title']}**")
                            st.write(f"Genres: {', '.join(rec['genres'])}")
                            st.write(f"{rec['overview'][:150]}...")
                        
                        with col2:
                            st.metric("Rating", f"{rec['vote_average']}/10")
                        
                        with col3:
                            st.metric("Similarity", f"{rec['similarity_score']:.3f}")
                        
                        st.divider()

elif page == "Browse by Genre":
    st.header("🎭 Browse by Genre")
    
    # Get available genres
    stats = recommender.get_stats()
    available_genres = stats["unique_genres"]
    
    # Genre selection
    selected_genre = st.selectbox("Select a genre:", available_genres)
    num_movies = st.slider("Number of movies to show:", min_value=1, max_value=30, value=15)
    
    if st.button("Browse Movies"):
        with st.spinner("Loading movies..."):
            movies = recommender.search_by_genre(selected_genre, num_movies)
            
            if not movies:
                st.warning(f"No movies found for genre '{selected_genre}'")
            else:
                st.subheader(f"🎬 Top {len(movies)} movies in '{selected_genre}' genre")
                
                # Display movies in a grid
                cols = st.columns(2)
                for i, movie in enumerate(movies):
                    with cols[i % 2]:
                        with st.container():
                            st.write(f"**{i+1}. {movie['title']}**")
                            
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"Genres: {', '.join(movie['genres'])}")
                                st.write(f"Release: {movie['release_date']}")
                            with col2:
                                st.metric("Rating", f"{movie['vote_average']}/10")
                            
                            st.write(f"{movie['overview'][:120]}...")
                            st.divider()

elif page == "Random Discovery":
    st.header("🎲 Random Movie Discovery")
    st.write("Discover random movies from our collection!")
    
    num_random = st.slider("Number of random movies:", min_value=1, max_value=15, value=8)
    
    if st.button("Discover Movies"):
        with st.spinner("Finding random movies..."):
            movies = recommender.get_random_movies(num_random)
            
            st.subheader(f"🎬 {len(movies)} Random Movies")
            
            # Display in grid
            cols = st.columns(2)
            for i, movie in enumerate(movies):
                with cols[i % 2]:
                    with st.container():
                        st.write(f"**{movie['title']}**")
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"Genres: {', '.join(movie['genres'])}")
                            st.write(f"Release: {movie['release_date']}")
                        with col2:
                            st.metric("Rating", f"{movie['vote_average']}/10")
                        
                        st.write(f"{movie['overview'][:150]}...")
                        
                        # Add "Get Similar" button
                        if st.button(f"Find Similar to {movie['title']}", key=f"similar_{movie['id']}"):
                            similar_movies = recommender.recommend_by_movie_id(movie['id'], 5)
                            st.write("**Similar movies:**")
                            for sim in similar_movies[:3]:
                                st.write(f"- {sim['title']} (Score: {sim['similarity_score']:.3f})")
                        
                        st.divider()

elif page == "Dataset Stats":
    st.header("📊 Dataset Statistics")
    
    stats = recommender.get_stats()
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Movies", stats["total_movies"])
    
    with col2:
        st.metric("Unique Genres", len(stats["unique_genres"]))
    
    with col3:
        st.metric("Avg Rating", f"{stats['avg_rating']:.2f}/10")
    
    with col4:
        st.metric("Feature Dimensions", stats["feature_dimensions"])
    
    # Genres breakdown
    st.subheader("Available Genres")
    genre_cols = st.columns(4)
    for i, genre in enumerate(stats["unique_genres"]):
        with genre_cols[i % 4]:
            st.write(f"• {genre}")
    
    # Rating distribution
    st.subheader("Movies by Rating Distribution")
    df = recommender.df
    
    # Create rating bins
    rating_bins = pd.cut(df['vote_average'], bins=[0, 3, 5, 7, 8, 10], labels=['Poor (0-3)', 'Fair (3-5)', 'Good (5-7)', 'Great (7-8)', 'Excellent (8-10)'])
    rating_counts = rating_bins.value_counts()
    
    # Display as metrics
    cols = st.columns(len(rating_counts))
    for i, (rating, count) in enumerate(rating_counts.items()):
        with cols[i]:
            st.metric(rating, count)
    
    # Top rated movies
    st.subheader("Top 10 Highest Rated Movies")
    top_movies = df.nlargest(10, 'vote_average')[['title', 'vote_average', 'vote_count']].copy()
    
    for i, (_, movie) in enumerate(top_movies.iterrows(), 1):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"{i}. **{movie['title']}**")
        with col2:
            st.write(f"{movie['vote_average']}/10")
        with col3:
            st.write(f"{movie['vote_count']} votes")

# Footer
st.markdown("---")
st.markdown(
    """
    **Movie Recommendation System** - Built with Streamlit
    
    This system uses content-based filtering with TF-IDF vectorization, 
    genre encoding, and cosine similarity to find movies similar to your preferences.
    """
)
