# 🚀 Deployment Guide - Movie Recommendation System

## Quick Deployment Options

### 1. 🌟 **Streamlit Cloud** (Recommended - Free & Easy)

**Steps:**
1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Movie Recommendation System"
git branch -M main
# Create repository on GitHub first, then:
git remote add origin https://github.com/yourusername/movie-recommendation-system.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect GitHub and select your repository
   - Set main file: `streamlit_app.py`
   - Click "Deploy!"

**Result:** Your app will be live at `https://yourusername-movie-recommendation-system.streamlit.app`

---

### 2. 🐳 **Docker** (Local or Cloud)

**Run locally:**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access:
# Streamlit app: http://localhost:8501
# API server: http://localhost:8000
```

**Deploy to cloud:**
- Push Docker image to DockerHub/AWS ECR
- Deploy on AWS ECS, Google Cloud Run, or DigitalOcean

---

### 3. ☁️ **Heroku** (Free tier available)

**Steps:**
```bash
# Install Heroku CLI first
heroku login
heroku create your-movie-app-name
git add .
git commit -m "Heroku deployment"
git push heroku main
```

**Result:** App live at `https://your-movie-app-name.herokuapp.com`

---

### 4. ⚡ **Vercel** (Fast deployment)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

---

### 5. 🔧 **Railway** (Modern platform)

1. Connect GitHub repo at [railway.app](https://railway.app)
2. Select Python template
3. Set start command: `streamlit run streamlit_app.py --server.port $PORT`
4. Deploy!

---

## 📁 Files Ready for Deployment

✅ `requirements.txt` - Dependencies  
✅ `Procfile` - Heroku process file  
✅ `Dockerfile` - Container configuration  
✅ `docker-compose.yml` - Multi-service setup  
✅ `setup.sh` - Streamlit configuration  

## 🔧 Environment Variables (if needed)

For production deployments, you might want to set:
```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## 📊 Performance Expectations

- **Startup time:** 10-30 seconds (preprocessing on first run)
- **Response time:** < 100ms for recommendations
- **Memory usage:** ~100MB
- **Concurrent users:** 50-100+ depending on hosting

## 🔒 Production Considerations

1. **Add authentication** for private deployments
2. **Use database** instead of JSON for larger datasets
3. **Add caching** (Redis) for better performance
4. **Monitor usage** with analytics
5. **Set up CI/CD** for automatic deployments

---

## 🏃‍♂️ Quick Start (Choose One)

### For Beginners - Streamlit Cloud:
1. `git init && git add . && git commit -m "init"`
2. Push to GitHub
3. Deploy on share.streamlit.io

### For Developers - Docker:
1. `docker-compose up --build`
2. Open http://localhost:8501

### For Production - Railway:
1. Connect GitHub to railway.app
2. Deploy with one click

---

**Need help?** Check the individual `DEPLOY_*.md` files for detailed instructions!
