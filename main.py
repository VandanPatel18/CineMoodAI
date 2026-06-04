"""Entrypoint instructions for CineMood AI.

Run the Streamlit UI with:

    streamlit run ui/streamlit_app.py

"""

import sys

def _print_help():
    print("CineMood AI: run the Streamlit UI:")
    print("    pip install -r requirements.txt")
    print("    streamlit run ui/streamlit_app.py")


if __name__ == '__main__':
    _print_help()

from models.semantic_model import SemanticMovieRecommender


recommender = SemanticMovieRecommender(
    movie_path="data/tmdb_5000_movies.csv",
    credits_path="data/tmdb_5000_credits.csv"
)

while True:

    print("\n" + "=" * 50)

    user_input = input(
        "How are you feeling today?\n\n"
    )

    if user_input.lower() == "exit":
        break

    recommendations = recommender.recommend_movies(
        user_input
    )

    print("\n🎬 Recommended Movies:\n")

    for i, movie in enumerate(recommendations, 1):

        print(f"{i}. {movie['title']}")
        print(f"⭐ Rating: {movie['rating']}")
        print(f"📝 {movie['overview'][:150]}...")
        print("-" * 50)
