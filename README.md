# Movie Recommendation System

A content-based movie recommendation system built with Python, scikit-learn, and Streamlit.

## Features

- Content-based filtering using TF-IDF and genre encoding
- Cosine similarity for movie recommendations
- Robust title search with fuzzy matching
- Genre-based browsing
- Random movie discovery
- Web interface with Streamlit
- CLI interface for quick testing

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Preprocess the data
```bash
python3 preprocess_movies.py
```

This will:
- Clean and normalize movie data
- Create TF-IDF features from movie overviews
- Encode genres using MultiLabelBinarizer
- Compute similarity matrix
- Save all artifacts for fast loading

### 2. Use the CLI interface
```bash
# Get recommendations by title
python3 cli.py --title "Interstellar" --num-recommendations 10

# Search by genre
python3 cli.py --genre "Action" --num-recommendations 5

# Get random movies
python3 cli.py --random --num-recommendations 8

# Show dataset statistics
python3 cli.py --stats
```

### 3. Use the web interface
```bash
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501`

## Deployment

### 🚀 Quick Deployment

**Option 1: Streamlit Cloud (Recommended)**
```bash
# Run the deployment helper
./deploy.sh

# Or manually:
git init && git add . && git commit -m "init"
# Push to GitHub, then deploy on share.streamlit.io
```

**Option 2: Docker**
```bash
docker-compose up --build
# Access: http://localhost:8501
```

**Option 3: One-click platforms**
- **Railway:** Connect GitHub repo at railway.app
- **Render:** Connect GitHub repo at render.com  
- **Heroku:** `heroku create && git push heroku main`

See `DEPLOYMENT.md` for detailed instructions.

---

## Files Structure

- `preprocess_movies.py` - Data preprocessing and feature engineering
- `movie_recommender.py` - Main recommendation engine
- `cli.py` - Command-line interface
- `streamlit_app.py` - Web interface
- `movies_dataset.json` - Movie dataset
- `artifacts/` - Preprocessed data and models
  - `movies_preprocessed.csv` - Cleaned movie data
  - `similarity_matrix.npy` - Precomputed similarity matrix
  - `genre_encoder.pkl` - Fitted genre encoder
  - `tfidf_vectorizer.pkl` - Fitted TF-IDF vectorizer
  - `rating_scaler.pkl` - Fitted rating scaler
  - `metadata.json` - Dataset metadata

## Algorithm

The system uses content-based filtering with:

1. **Text Features**: TF-IDF vectorization of movie overviews with n-grams (1-2)
2. **Genre Features**: MultiLabelBinarizer encoding of movie genres
3. **Rating Features**: Normalized vote average and vote count
4. **Similarity**: Cosine similarity between combined feature vectors

## API

### MovieRecommender Class

```python
from movie_recommender import MovieRecommender

recommender = MovieRecommender()

# Get recommendations by title
result = recommender.recommend_by_title("Interstellar", 10)

# Get recommendations by movie ID
recommendations = recommender.recommend_by_movie_id(157336, 10)

# Search by genre
movies = recommender.search_by_genre("Action", 20)

# Get random movies
random_movies = recommender.get_random_movies(5)
```

## Dataset

The system works with movie data in JSON format with the following fields:
- `id`: Unique movie identifier
- `title`: Movie title
- `genres`: List of movie genres
- `overview`: Movie plot summary
- `vote_average`: Average user rating
- `vote_count`: Number of user votes
- `release_date`: Movie release date

## Performance

- Preprocessing: ~1-2 seconds for 60 movies
- Recommendation: ~10ms per query (using precomputed similarity matrix)
- Memory usage: ~50MB for 60 movies with similarity matrix

## Deployment

The system is ready for deployment with:
- Streamlit Cloud
- Heroku
- Docker
- Any Python hosting service

For production deployment, consider:
- Using a database for movie storage
- Implementing caching for popular queries
- Adding user authentication and rating collection
- Implementing collaborative filtering for hybrid recommendations
# movie-recommender
