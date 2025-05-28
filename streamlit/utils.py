import requests
import os
import streamlit as st

API_KEY = os.getenv("TMDB_API_KEY") or st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"

def get_genres():
    url = f"{BASE_URL}/genre/movie/list"
    params = {"api_key": API_KEY, "language": "ko"}
    res = requests.get(url, params=params).json()
    return {g["name"]: g["id"] for g in res["genres"]}

def get_movies(genre_id, start_year, end_year, sort_by="vote_average.desc"):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "with_genres": genre_id,
        "language": "ko",
        "sort_by": sort_by,
        "vote_count.gte": 50,
        "primary_release_date.gte": f"{start_year}-01-01",
        "primary_release_date.lte": f"{end_year}-12-31",
        "page": 1
    }
    res = requests.get(url, params=params).json()
    return res.get("results", [])[:10]

def get_similar_movies(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/similar"
    params = {"api_key": API_KEY, "language": "ko"}
    res = requests.get(url, params=params).json()
    return res.get("results", [])[:5]

def get_mood_genres():
    return {
        "우울": ["코미디", "가족"],
        "기분전환": ["액션", "모험"],
        "감성적인": ["드라마", "로맨스"],
        "지루할 때": ["SF", "스릴러"],
        "짜릿하게": ["공포", "미스터리"]
    }

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "append_to_response": "credits,videos",
        "language": "ko"
    }
    res = requests.get(url, params=params).json()
    director = next((c["name"] for c in res["credits"]["crew"] if c["job"] == "Director"), "정보 없음")
    cast = ", ".join([c["name"] for c in res["credits"]["cast"][:3]]) or "정보 없음"
    runtime = res.get("runtime", "알 수 없음")
    videos = res.get("videos", {}).get("results", [])
    trailer = next((v for v in videos if v["type"] == "Trailer" and v["site"] == "YouTube"), None)
    trailer_url = f"https://www.youtube.com/watch?v={trailer['key']}" if trailer else None
    return director, cast, runtime, trailer_url

def get_watch_providers(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": API_KEY}
    res = requests.get(url, params=params).json()
    providers = res.get("results", {}).get("KR", {}).get("flatrate", [])
    return [p["provider_name"] for p in providers]

def render_stars(vote_average: float) -> str:
    stars = int(round(vote_average / 2))  # 5점 만점 기준
    return "⭐" * stars + "☆" * (5 - stars)
