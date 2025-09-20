# Streamlit Cloud Deployment

## Prerequisites
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy your app

## Steps:

### 1. Create a GitHub Repository
```bash
cd /Users/amineouhiba/Desktop/recommendationSystemMovies
git init
git add .
git commit -m "Initial commit: Movie Recommendation System"
git branch -M main
git remote add origin https://github.com/yourusername/movie-recommendation-system.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Set main file path: `streamlit_app.py`
5. Click "Deploy!"

### 3. App will be available at:
`https://yourusername-movie-recommendation-system-streamlit-app-xxxxx.streamlit.app`

## Note: 
The preprocessing will run automatically on first deployment since artifacts/ folder will be empty.
