#!/usr/bin/env python3
"""
Movie Recommendation System - Setup and Run Script
"""

import subprocess
import sys
import os
import argparse

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Movie Recommendation System Runner")
    parser.add_argument("--setup", action="store_true", help="Run initial setup (preprocessing)")
    parser.add_argument("--streamlit", action="store_true", help="Run Streamlit web app")
    parser.add_argument("--fastapi", action="store_true", help="Run FastAPI server")
    parser.add_argument("--cli", action="store_true", help="Run CLI demo")
    parser.add_argument("--all", action="store_true", help="Run complete demo")
    
    args = parser.parse_args()
    
    # Get the Python executable path (works locally and in deployment)
    python_path = sys.executable
    
    if args.setup or args.all:
        print("🚀 Setting up Movie Recommendation System")
        if not run_command(f"{python_path} preprocess_movies.py", "Running preprocessing"):
            sys.exit(1)
    
    if args.cli or args.all:
        print("\n🎬 CLI Demo")
        print("\n1. Testing movie search:")
        run_command(f'{python_path} cli.py --title "Interstellar" --num-recommendations 3', "Searching for Interstellar")
        
        print("\n2. Testing genre search:")
        run_command(f'{python_path} cli.py --genre "Action" --num-recommendations 3', "Searching Action movies")
        
        print("\n3. Testing random discovery:")
        run_command(f'{python_path} cli.py --random --num-recommendations 2', "Getting random movies")
        
        print("\n4. Dataset statistics:")
        run_command(f'{python_path} cli.py --stats', "Showing dataset stats")
    
    if args.streamlit:
        print("\n🌐 Starting Streamlit Web App")
        print("The web app will open in your browser at http://localhost:8501")
        os.system(f"{python_path} -m streamlit run streamlit_app.py")
    
    if args.fastapi:
        print("\n🔌 Starting FastAPI Server")
        print("API documentation will be available at http://localhost:8000/docs")
        os.system(f"{python_path} -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload")
    
    if not any([args.setup, args.streamlit, args.fastapi, args.cli, args.all]):
        print("Movie Recommendation System")
        print("\nUsage:")
        print("  python3 run.py --setup          # Run initial preprocessing")
        print("  python3 run.py --cli            # Run CLI demo")
        print("  python3 run.py --streamlit      # Run web app")
        print("  python3 run.py --fastapi        # Run API server")
        print("  python3 run.py --all            # Run complete demo")
        print("\nFor more options:")
        print("  python3 cli.py --help")

if __name__ == "__main__":
    main()
