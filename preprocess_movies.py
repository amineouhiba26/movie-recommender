import pandas as pd
import json
import numpy as np
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import scipy.sparse as sp

def clean_genres(genres_list):
    """Clean and normalize genre data"""
    if genres_list is None or (isinstance(genres_list, float) and pd.isna(genres_list)):
        return []
    if isinstance(genres_list, str):
        return [genres_list.strip()]
    if isinstance(genres_list, list):
        return [genre.strip() for genre in genres_list if genre and str(genre).strip()]
    return []

def preprocess_movies(apply_svd=False, svd_components=100):
    """
    Preprocess movies data with improved feature engineering
    """
    print("Loading dataset...")
    
    # Step 1: Load dataset
    with open("movies_dataset.json", "r", encoding="utf-8") as f:
        movies = json.load(f)
    
    df = pd.DataFrame(movies)
    print(f"Loaded {len(df)} movies")
    
    # Step 2: Clean and normalize data
    df["overview"] = df["overview"].fillna("").astype(str)
    df["title"] = df["title"].astype(str)
    df["genres"] = df["genres"].apply(clean_genres)
    
    # Create normalized title for better searching
    df["title_normalized"] = df["title"].str.lower().str.strip()
    
    # Handle missing values
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)
    
    print("Encoding genres...")
    
    # Step 3: Encode genres with better handling
    mlb = MultiLabelBinarizer()
    genres_encoded = mlb.fit_transform(df["genres"])
    genres_df = pd.DataFrame(genres_encoded, columns=mlb.classes_)
    
    print(f"Found {len(mlb.classes_)} unique genres: {list(mlb.classes_)}")
    
    # Step 4: TF-IDF on overview with improved parameters
    print("Creating TF-IDF features...")
    tfidf = TfidfVectorizer(
        stop_words="english", 
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8
    )
    overview_tfidf = tfidf.fit_transform(df["overview"])
    
    # Step 5: Add rating features
    scaler = StandardScaler()
    rating_features = scaler.fit_transform(df[["vote_average", "vote_count"]].values)
    
    # Step 6: Combine features
    print("Combining features...")
    combined_features = sp.hstack([
        overview_tfidf,
        genres_encoded,
        rating_features
    ])
    
    # Step 7: Optional SVD for dimensionality reduction
    if apply_svd and svd_components < combined_features.shape[1]:
        print(f"Applying SVD with {svd_components} components...")
        svd = TruncatedSVD(n_components=svd_components, random_state=42)
        combined_features = svd.fit_transform(combined_features)
    else:
        svd = None
    
    # Step 8: Calculate similarity matrix
    print("Computing similarity matrix...")
    similarity_matrix = cosine_similarity(combined_features)
    
    # Step 9: Save all artifacts
    print("Saving artifacts...")
    
    # Create artifacts directory
    os.makedirs("artifacts", exist_ok=True)
    
    # Save preprocessed dataframe
    df.to_csv("artifacts/movies_preprocessed.csv", index=False)
    
    # Save similarity matrix
    np.save("artifacts/similarity_matrix.npy", similarity_matrix)
    
    # Save fitted transformers
    joblib.dump(mlb, "artifacts/genre_encoder.pkl")
    joblib.dump(tfidf, "artifacts/tfidf_vectorizer.pkl")
    joblib.dump(scaler, "artifacts/rating_scaler.pkl")
    
    if svd:
        joblib.dump(svd, "artifacts/svd_transformer.pkl")
    
    # Save metadata
    metadata = {
        "total_movies": len(df),
        "unique_genres": list(mlb.classes_),
        "feature_dimensions": combined_features.shape[1],
        "tfidf_features": overview_tfidf.shape[1],
        "genre_features": genres_encoded.shape[1],
        "rating_features": 2,
        "svd_applied": apply_svd,
        "svd_components": svd_components if apply_svd else None
    }
    
    with open("artifacts/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("Preprocessing completed successfully!")
    print(f"Movies processed: {len(df)}")
    print(f"Similarity matrix shape: {similarity_matrix.shape}")
    print(f"Feature dimensions: {combined_features.shape[1]}")
    print(f"Artifacts saved to 'artifacts/' directory")
    
    return df, similarity_matrix, metadata

if __name__ == "__main__":
    preprocess_movies(apply_svd=False)
