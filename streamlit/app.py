import streamlit as st
import pandas as pd
import altair as alt
from utils import (
    get_genres, get_movies, render_stars, get_mood_genres,
    get_movie_details, get_watch_providers
)

st.set_page_config(page_title="영화 추천 시스템", layout="wide")
st.title("🎬 영화 추천 시스템")

# 상태 초기화
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

genres = get_genres()
mood_genres = get_mood_genres()

tab1, tab2, tab3 = st.tabs(["📌 기본 추천", "🧠 기분 추천", "❤️ 찜한 영화"])

# 📌 기본 추천
with tab1:
    sort_option = st.radio("정렬 기준 선택", ["평점순", "인기순"], horizontal=True)
    sort_by = "vote_average.desc" if sort_option == "평점순" else "popularity.desc"
    genre_name = st.selectbox("장르 선택", list(genres.keys()))
    genre_id = genres[genre_name]
    year_range = st.slider("연도 범위", 1980, 2025, (2020, 2025))
    movies = get_movies(genre_id, year_range[0], year_range[1], sort_by)

    if movies:
        st.subheader(f"{sort_option} 기준 TOP 10 영화 ({genre_name})")
        df = pd.DataFrame([{"제목": m["title"], "평점": m["vote_average"]} for m in movies])
        # 기본 바 차트
        bar = alt.Chart(df).mark_bar(
            color="#b39ddb",
            cornerRadiusTopRight=3,
            cornerRadiusBottomRight=3
        ).encode(
            x=alt.X("평점:Q", scale=alt.Scale(domain=(0, 10)), title="평점"),
            y=alt.Y("제목:N", sort='-x', title="영화 제목"),
            tooltip=[alt.Tooltip("제목:N"), alt.Tooltip("평점:Q")]
        )

        # 텍스트 라벨
        text = alt.Chart(df).mark_text(
            align="left",
            baseline="middle",
            dx=3,
            fontSize=12,
            fontWeight="bold",
            color="#5e35b1"
        ).encode(
            x="평점:Q",
            y=alt.Y("제목:N", sort='-x'),
            text=alt.Text("평점:Q", format=".1f")
        )

        # 차트 합치기 → 이곳에 configure 적용!
        chart = (bar + text).properties(
            height=400,
            title="🎯 평점 기준 TOP 10 영화"
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=18,
            anchor="start"
        )

        st.altair_chart(chart, use_container_width=True)


        for movie in movies:
            cols = st.columns([1, 3])
            with cols[0]:
                if movie.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w200{movie['poster_path']}")
            with cols[1]:
                st.markdown(f"**{movie['title']}**")
                st.markdown(f"{render_stars(movie['vote_average'])} ({movie['vote_average']:.1f})점  \n📅 {movie.get('release_date', 'N/A')}")
                st.caption(movie.get("overview", "줄거리 없음."))

                # 찜하기
                if st.button("❤️ 찜하기", key=f"fav_{movie['id']}"):
                    st.session_state["favorites"].append(movie)

                # OTT 제공 여부
                providers = get_watch_providers(movie["id"])
                if providers:
                    st.info("📺 제공 중: " + ", ".join(providers))
                else:
                    st.warning("📺 OTT 미제공")

                # 예고편 보기
                if st.button("🎥 예고편 보기", key=f"trailer_{movie['id']}"):
                    _, _, _, trailer_url = get_movie_details(movie["id"])
                    if trailer_url:
                        st.video(trailer_url)
                    else:
                        st.warning("예고편을 찾을 수 없습니다.")

                # 상세 정보
                with st.expander("🎬 상세 정보 보기"):
                    director, cast, runtime, _ = get_movie_details(movie["id"])
                    st.markdown(f"🎞️ 러닝타임: {runtime}분")
                    st.markdown(f"🎬 감독: {director}")
                    st.markdown(f"🎭 출연진: {cast}")

# 🧠 기분 기반 추천
with tab2:
    mood = st.selectbox("오늘 기분은 어떤가요?", list(mood_genres.keys()))
    genre_list = mood_genres[mood]
    genre_ids = [genres[g] for g in genre_list if g in genres]
    year_range = st.slider("연도 범위", 1980, 2025, (2015, 2025))
    all_movies = []
    for gid in genre_ids:
        all_movies += get_movies(gid, year_range[0], year_range[1])
    if all_movies:
        for movie in all_movies[:10]:
            cols = st.columns([1, 3])
            with cols[0]:
                if movie.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w200{movie['poster_path']}")
            with cols[1]:
                st.markdown(f"**{movie['title']}**")
                st.markdown(f"⭐ {movie['vote_average']}점  \n📅 {movie.get('release_date', 'N/A')}")
                st.caption(movie.get("overview", "줄거리 없음."))

# ❤️ 찜한 영화
with tab3:
    st.header("내가 찜한 영화 ❤️")
    if not st.session_state["favorites"]:
        st.info("아직 찜한 영화가 없습니다.")
    for movie in st.session_state["favorites"]:
        st.markdown(f"**{movie['title']}** - ⭐ {movie['vote_average']}")
