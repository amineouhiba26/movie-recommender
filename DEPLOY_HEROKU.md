# Heroku Deployment

## Prerequisites
- Heroku CLI installed
- Heroku account

## Steps:

### 1. Create Heroku-specific files

Create `Procfile`:
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

### 2. Deploy to Heroku
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-movie-recommender-app

# Set buildpack
heroku buildpacks:set heroku/python

# Deploy
git add .
git commit -m "Heroku deployment setup"
git push heroku main
```

### 3. App will be available at:
`https://your-movie-recommender-app.herokuapp.com`
