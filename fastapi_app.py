from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from movie_recommender import MovieRecommender
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Movie Recommendation API",
    description="A content-based movie recommendation system API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender
try:
    recommender = MovieRecommender()
except FileNotFoundError:
    recommender = None

# Pydantic models
class MovieResponse(BaseModel):
    id: int
    title: str
    genres: List[str]
    overview: str
    vote_average: float
    vote_count: int
    release_date: str
    similarity_score: Optional[float] = None

class RecommendationResponse(BaseModel):
    query: str
    matched_movie: MovieResponse
    other_matches: List[dict]
    recommendations: List[MovieResponse]

class StatsResponse(BaseModel):
    total_movies: int
    unique_genres: List[str]
    avg_rating: float
    feature_dimensions: int

# API endpoints
@app.get("/")
async def root():
    return {"message": "Movie Recommendation API", "status": "running"}

@app.get("/health")
async def health_check():
    if recommender is None:
        raise HTTPException(status_code=500, detail="Recommender not initialized. Run preprocess_movies.py first.")
    return {"status": "healthy", "movies_loaded": len(recommender.df)}

@app.get("/recommendations/title/{title}", response_model=RecommendationResponse)
async def recommend_by_title(title: str, limit: int = 10):
    """Get movie recommendations based on title"""
    if recommender is None:
        raise HTTPException(status_code=500, detail="Recommender not initialized")
    
    try:
        result = recommender.recommend_by_title(title, limit)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        # Convert to response format
        matched_movie = MovieResponse(**result["matched_movie"])
        recommendations = [MovieResponse(**rec) for rec in result["recommendations"]]
        
        return RecommendationResponse(
            query=result["query"],
            matched_movie=matched_movie,
            other_matches=result["other_matches"],
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/id/{movie_id}")
async def recommend_by_id(movie_id: int, limit: int = 10):
    """Get movie recommendations based on movie ID"""
    if recommender is None:
        raise HTTPException(status_code=500, detail="Recommender not initialized")
    
    try:
        recommendations = recommender.recommend_by_movie_id(movie_id, limit)
        return {"recommendations": [MovieResponse(**rec) for rec in recommendations]}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies/genre/{genre}")
async def search_by_genre(genre: str, limit: int = 20):
    """Search movies by genre"""
    if recommender is None:
        raise HTTPException(status_code=500, detail="Recommender not initialized")
    
    try:
        movies = recommender.search_by_genre(genre, limit)
        return {"movies": [MovieResponse(**movie) for movie in movies]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies/random")
async def get_random_movies(limit: int = 5):
    """Get random movies"""
    if recommender is None:
        raise HTTPException(status_code=500, detail="Recommender not initialized")
    
    try:
        movies = recommender.get_random_movies(limit)
        return {"movies": [MovieResponse(**movie) for movie in movies]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies/{movie_id}")
async def get_movie_info(movie_id: int):
    """Get detailed movie information"""
    if recommender is None:
        raise HTTPException(status_code=500, detail="Recommender not initialized")
    
    try:
        movie = recommender.get_movie_info(movie_id)
        if movie is None:
            raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
        
        return MovieResponse(**movie)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get dataset statistics"""
    if recommender is None:
        raise HTTPException(status_code=500, detail="Recommender not initialized")
    
    try:
        stats = recommender.get_stats()
        return StatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/genres")
async def get_available_genres():
    """Get list of available genres"""
    if recommender is None:
        raise HTTPException(status_code=500, detail="Recommender not initialized")
    
    try:
        stats = recommender.get_stats()
        return {"genres": stats["unique_genres"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
