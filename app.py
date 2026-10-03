import streamlit as st
import pickle
import pandas as pd
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 🔑 API KEY
API_KEY = "f01ed4f75221db45cdc73b6e5201deaa"

# ✅ Session with retry (FIXES CONNECTION ERROR)
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504]
)
session.mount("https://", HTTPAdapter(max_retries=retries))

# ✅ headers (prevents blocking)
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ✅ cache (faster loading, avoids repeated API calls)
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        if movie_id is None:
            return "https://via.placeholder.com/300x450?text=No+Image"

        url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={API_KEY}&language=en-US"

        response = session.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return "https://via.placeholder.com/300x450?text=No+Image"

        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"

    except Exception as e:
        print("Error:", e)
        return "https://via.placeholder.com/300x450?text=No+Image"


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_row = movies.iloc[i[0]]

        movie_id = movie_row.get('movie_id')

        recommended_movies.append(movie_row.title)
        recommended_movies_posters.append(fetch_poster(movie_id))

        time.sleep(0.2)  # ✅ prevents API overload

    return recommended_movies, recommended_movies_posters


# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# UI
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie:',
    movies['title'].values
)

if st.button('Show Recommendation'):
    recommended_movies, recommended_movies_posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for idx in range(len(recommended_movies)):
        with cols[idx]:
            st.text(recommended_movies[idx])
            st.image(recommended_movies_posters[idx])