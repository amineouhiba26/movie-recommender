#!/usr/bin/env python3
"""
Simple CLI for Movie Recommendation System
"""

import argparse
import sys
from movie_recommender import MovieRecommender

def main():
    parser = argparse.ArgumentParser(description="Movie Recommendation System CLI")
    parser.add_argument("--title", "-t", type=str, help="Movie title to get recommendations for")
    parser.add_argument("--movie-id", "-i", type=int, help="Movie ID to get recommendations for")
    parser.add_argument("--genre", "-g", type=str, help="Search movies by genre")
    parser.add_argument("--random", "-r", action="store_true", help="Get random movies")
    parser.add_argument("--num-recommendations", "-n", type=int, default=10, help="Number of recommendations (default: 10)")
    parser.add_argument("--stats", "-s", action="store_true", help="Show dataset statistics")
    
    args = parser.parse_args()
    
    try:
        recommender = MovieRecommender()
        
        if args.stats:
            stats = recommender.get_stats()
            print("Dataset Statistics:")
            print(f"Total movies: {stats['total_movies']}")
            print(f"Average rating: {stats['avg_rating']:.2f}")
            print(f"Unique genres: {len(stats['unique_genres'])}")
            print(f"Available genres: {', '.join(stats['unique_genres'])}")
            return
        
        if args.title:
            print(f"Getting recommendations for movie title: '{args.title}'")
            result = recommender.recommend_by_title(args.title, args.num_recommendations)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                return
            
            matched_movie = result["matched_movie"]
            print(f"\nMatched Movie: {matched_movie['title']} (ID: {matched_movie['id']})")
            print(f"Genres: {', '.join(matched_movie['genres'])}")
            print(f"Rating: {matched_movie['vote_average']}/10 ({matched_movie['vote_count']} votes)")
            print(f"Overview: {matched_movie['overview'][:200]}...")
            
            if result["other_matches"]:
                print(f"\nOther possible matches:")
                for match in result["other_matches"][:3]:
                    print(f"- {match['title']} (Score: {match['score']:.2f})")
            
            print(f"\nTop {len(result['recommendations'])} Recommendations:")
            for i, rec in enumerate(result["recommendations"], 1):
                print(f"{i:2d}. {rec['title']}")
                print(f"    Genres: {', '.join(rec['genres'])}")
                print(f"    Rating: {rec['vote_average']}/10 | Similarity: {rec['similarity_score']:.3f}")
                print()
        
        elif args.movie_id:
            print(f"Getting recommendations for movie ID: {args.movie_id}")
            try:
                recommendations = recommender.recommend_by_movie_id(args.movie_id, args.num_recommendations)
                movie_info = recommender.get_movie_info(args.movie_id)
                
                print(f"\nBase Movie: {movie_info['title']}")
                print(f"Genres: {', '.join(movie_info['genres'])}")
                print(f"Rating: {movie_info['vote_average']}/10")
                
                print(f"\nTop {len(recommendations)} Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i:2d}. {rec['title']}")
                    print(f"    Genres: {', '.join(rec['genres'])}")
                    print(f"    Rating: {rec['vote_average']}/10 | Similarity: {rec['similarity_score']:.3f}")
                    print()
                    
            except ValueError as e:
                print(f"Error: {e}")
        
        elif args.genre:
            print(f"Searching movies by genre: '{args.genre}'")
            movies = recommender.search_by_genre(args.genre, args.num_recommendations)
            
            if not movies:
                print(f"No movies found for genre '{args.genre}'")
                return
            
            print(f"\nTop {len(movies)} movies in '{args.genre}' genre:")
            for i, movie in enumerate(movies, 1):
                print(f"{i:2d}. {movie['title']}")
                print(f"    Genres: {', '.join(movie['genres'])}")
                print(f"    Rating: {movie['vote_average']}/10 ({movie['vote_count']} votes)")
                print()
        
        elif args.random:
            print("Getting random movies for exploration:")
            movies = recommender.get_random_movies(args.num_recommendations)
            
            for i, movie in enumerate(movies, 1):
                print(f"{i}. {movie['title']}")
                print(f"   Genres: {', '.join(movie['genres'])}")
                print(f"   Rating: {movie['vote_average']}/10")
                print(f"   Overview: {movie['overview'][:150]}...")
                print()
        
        else:
            print("Please specify one of the following options:")
            print("  --title 'Movie Name'     Get recommendations by movie title")
            print("  --movie-id 12345         Get recommendations by movie ID")
            print("  --genre 'Action'         Search movies by genre")
            print("  --random                 Get random movies")
            print("  --stats                  Show dataset statistics")
            print("\nUse --help for more options.")
    
    except FileNotFoundError:
        print("Error: Preprocessed data not found. Please run preprocess_movies.py first:")
        print("  python3 preprocess_movies.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
