#!/bin/bash

# Movie Recommendation System - Easy Deployment Script

echo "🎬 Movie Recommendation System - Deployment Helper"
echo "================================================="

function deploy_streamlit_cloud() {
    echo "📋 Streamlit Cloud Deployment Steps:"
    echo "1. Push your code to GitHub:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Movie Recommendation System'"
    echo "   git branch -M main"
    echo "   git remote add origin https://github.com/yourusername/repo-name.git"
    echo "   git push -u origin main"
    echo ""
    echo "2. Go to https://share.streamlit.io"
    echo "3. Click 'New app' and connect your GitHub repo"
    echo "4. Set main file: streamlit_app.py"
    echo "5. Click 'Deploy!'"
    echo ""
    echo "🌟 Your app will be live at: https://yourusername-repo-name.streamlit.app"
}

function deploy_docker() {
    echo "🐳 Building Docker container..."
    docker build -t movie-recommender .
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker build successful!"
        echo "🚀 Starting container..."
        docker run -p 8501:8501 movie-recommender &
        echo "📱 App will be available at: http://localhost:8501"
        echo "⏳ Wait 30 seconds for app to start, then open your browser"
    else
        echo "❌ Docker build failed"
    fi
}

function deploy_heroku() {
    echo "☁️ Heroku Deployment Steps:"
    echo "1. Install Heroku CLI if not installed"
    echo "2. heroku login"
    echo "3. heroku create your-app-name"
    echo "4. git add . && git commit -m 'Deploy to Heroku'"
    echo "5. git push heroku main"
    echo ""
    echo "🌟 Your app will be live at: https://your-app-name.herokuapp.com"
}

function show_requirements() {
    echo "📋 Deployment Requirements Check:"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        echo "✅ Python3: $(python3 --version)"
    else
        echo "❌ Python3 not found"
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        echo "✅ Git: $(git --version)"
    else
        echo "❌ Git not found"
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        echo "✅ Docker: $(docker --version)"
    else
        echo "❌ Docker not found"
    fi
    
    # Check files
    echo ""
    echo "📁 Required files:"
    files=("streamlit_app.py" "movie_recommender.py" "preprocess_movies.py" "requirements.txt" "movies_dataset.json")
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo "✅ $file"
        else
            echo "❌ $file"
        fi
    done
}

# Main menu
echo "Choose deployment option:"
echo "1) 🌟 Streamlit Cloud (Recommended - Free)"
echo "2) 🐳 Docker (Local test)"
echo "3) ☁️ Heroku (Cloud platform)"
echo "4) 📋 Check requirements"
echo "5) 📖 View full deployment guide"

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        deploy_streamlit_cloud
        ;;
    2)
        deploy_docker
        ;;
    3)
        deploy_heroku
        ;;
    4)
        show_requirements
        ;;
    5)
        echo "📖 Opening deployment guide..."
        cat DEPLOYMENT.md
        ;;
    *)
        echo "Invalid choice. Run script again."
        ;;
esac
