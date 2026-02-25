import streamlit as st
import pandas as pd
from collections import Counter

# Функция жанров (вставь свою полностью)
def extract_genres(text):
    if pd.isna(text) or not text:
        return ['другое']
    text = str(text).lower()
    genres = set()
    if any(w in text for w in ['драма', 'трагичн', 'эмоциональн']):
        genres.add('драма')
    # ... все твои остальные условия
    return list(genres) if genres else ['другое']

@st.cache_data
def load_data():
    df = pd.read_csv('kinopoisk-top250.csv')
    df['genres'] = df['overview'].apply(extract_genres)
    df['rating_ball'] = pd.to_numeric(df['rating_ball'], errors='coerce')
    return df.dropna(subset=['movie', 'year', 'rating_ball', 'url_logo'])

df = load_data()

st.title("Рекомендации фильмов по жанру")
st.subheader("Kinopoisk Top-250")

st.write("Популярные жанры:")
flat = [g for sub in df['genres'] for g in sub]
top = Counter(flat).most_common(10)
st.write(", ".join([f"{g} ({c})" for g, c in top]))

query = st.text_input("Жанр(ы) через запятую", "")

if query:
    user_g = [g.strip().lower() for g in query.split(',') if g.strip()]
    def matches(gs):
        return len(set(g.lower() for g in gs) & set(user_g))
    
    temp = df.copy()
    temp['matches'] = temp['genres'].apply(matches)
    
    result = temp[
        (temp['matches'] > 0) & (temp['rating_ball'] >= 7.8)
    ].sort_values(['matches', 'rating_ball'], ascending=[False, False]).head(8)
    
    if result.empty:
        st.warning("Ничего не найдено")
    else:
        st.success(f"Найдено {len(result)} фильмов")
        for i, r in result.iterrows():
            cols = st.columns([1, 4])
            with cols[0]:
                try:
                    st.image(r['url_logo'], width=140)
                except:
                    st.image("https://via.placeholder.com/140x210?text=Poster")
            with cols[1]:
                st.markdown(f"**{i+1}. {r['movie']} ({r['year']})** ★ {r['rating_ball']:.3f}")
                st.caption(f"реж. {r.get('director', '—')}")
                st.caption(f"Жанры: {', '.join(r['genres'])}")
                st.write(r['overview'][:250] + "..." if len(r['overview']) > 250 else r['overview'])
