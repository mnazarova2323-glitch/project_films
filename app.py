import streamlit as st
import pandas as pd
from collections import Counter

# Функция жанров (вставь свою полностью)
def extract_genres(text):
    if pd.isna(text) or not text:
        return ['другое']
    
    text = str(text).lower()
    genres = set()
    
    # Драма — основные слова из реальных описаний
    if any(w in text for w in ['драма', 'драматическ', 'трагич', 'эмоциональн', 'тяжёл', 'жизненн', 'судьба', 'человеческ', 'душ', 'потеря', 'страдан', 'одиночеств']):
        genres.add('драма')
    
    # Комедия
    if any(w in text for w in ['комед', 'комическ', 'юмор', 'смешн', 'весёл', 'пароди', 'сатир', 'шутк', 'смеётся', 'смешлив', 'абсурд']):
        genres.add('комедия')
    
    # Фантастика / sci-fi — расширяем сильно
    if any(w in text for w in ['фантастик', 'фантастика', 'научн', 'космос', 'будущ', 'времени', 'машин времени', 'подсознани', 'снов', 'сна', 'инициаци', 'идея', 'внедр', 'матриц', 'интерстеллар', 'планет', 'вселенн', 'чёрн дыра', 'космическ', 'альтернативн реальн', 'робот', 'киборг', 'искусствен интеллект']):
        genres.add('фантастика')
    
    # Приключения
    if any(w in text for w in ['приключен', 'путешеств', 'экспедиц', 'сокровищ', 'остров', 'море', 'джунгл', 'пират', 'квест', 'поиск', 'опасн', 'открыт', 'карт']):
        genres.add('приключения')
    
    # Криминал / детектив
    if any(w in text for w in ['криминал', 'мафи', 'банд', 'преступлен', 'ограблен', 'вор', 'убийств', 'детектив', 'бойцовск', 'преступник', 'полицейск', 'расслед', 'преступн', 'наркот', 'коррупц']):
        genres.add('криминал')
    
    # Триллер / психологический
    if any(w in text for w in ['триллер', 'саспенс', 'напряжён', 'психологическ', 'безуми', 'преслед', 'тайна', 'престиж', 'страх', 'загадк', 'интриг', 'подозр', 'обман', 'иллюз']):
        genres.add('триллер')
    
    # Мультфильм / анимация
    if any(w in text for w in ['мульт', 'анимац', 'детск', 'сказк', 'животн', 'лев', 'робот', 'игрушк', 'пиксар', 'коко', 'вверх', 'мультфильм', 'анимацион', 'мультяшн']):
        genres.add('мультфильм')
    
    # Военный
    if any(w in text for w in ['военн', 'войн', 'солдат', 'партизан', 'нацист', 'концлаг', 'фронт', 'старики', 'войска', 'битв', 'танки', 'арми', 'фашист']):
        genres.add('военный')
    
    # Исторический / биография
    if any(w in text for w in ['истори', 'биограф', 'реальн', 'произошл', 'прошл', 'древн', 'майя', 'шпион', 'средневеков', 'история', 'корол', 'император', 'революц']):
        genres.add('исторический')
    
    # Ужасы
    if any(w in text for w in ['ужас', 'страшн', 'страх', 'монстр', 'зомби', 'призрак', 'кровь', 'пугающ', 'жутк', 'демон']):
        genres.add('ужасы')
    
    # Мелодрама / романтика
    if any(w in text for w in ['мелодрама', 'любов', 'романтич', 'чувств', 'влюблён', 'сердц', 'роман', 'отношен', 'поцел', 'объят', 'ревнив']):
        genres.add('мелодрама')
    
    # Боевик / экшн
    if any(w in text for w in ['боевик', 'экшн', 'драка', 'погон', 'взрыв', 'герой', 'спасен', 'оружи', 'стрельб', 'бой', 'смертельн']):
        genres.add('боевик')
    
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
