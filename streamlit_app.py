import streamlit as st
from typing import List, Dict, Any


MOVIES: List[Dict[str, Any]] = [
    {
        "title": "3 Idiots",
        "genre": ["Comedy", "Drama"],
        "language": "Hindi",
        "rating": 8.4,
        "summary": "Three friends navigate engineering college and life lessons.",
        "actors": ["Aamir Khan"],
        "mood": ["inspirational", "feel-good"],
    },
    {
        "title": "Dangal",
        "genre": ["Biography", "Drama", "Sport"],
        "language": "Hindi",
        "rating": 8.4,
        "summary": "A father's quest to train his daughters into world-class wrestlers.",
        "actors": ["Aamir Khan"],
        "mood": ["inspirational"],
    },
    {
        "title": "Gully Boy",
        "genre": ["Drama", "Music"],
        "language": "Hindi",
        "rating": 7.9,
        "summary": "An aspiring rapper rises from Mumbai's streets.",
        "actors": ["Ranveer Singh"],
        "mood": ["energetic"],
    },
    {
        "title": "KGF: Chapter 1",
        "genre": ["Action", "Drama"],
        "language": "Kannada",
        "rating": 8.2,
        "summary": "A young man's journey to power in the Kolar gold fields.",
        "actors": ["Yash"],
        "mood": ["intense", "action"],
    },
    {
        "title": "Lucia",
        "genre": ["Thriller", "Drama"],
        "language": "Kannada",
        "rating": 7.7,
        "summary": "A psychological tale blending dreams and reality.",
        "actors": ["Sruthi Hariharan"],
        "mood": ["thoughtful", "mystery"],
    },
    {
        "title": "The Shawshank Redemption",
        "genre": ["Drama"],
        "language": "English",
        "rating": 9.3,
        "summary": "Two imprisoned men form a lasting friendship and find hope.",
        "actors": ["Tim Robbins", "Morgan Freeman"],
        "mood": ["inspirational"],
    },
    {
        "title": "Inception",
        "genre": ["Action", "Sci-Fi"],
        "language": "English",
        "rating": 8.8,
        "summary": "A thief who steals secrets through dream-sharing must plant an idea.",
        "actors": ["Leonardo DiCaprio"],
        "mood": ["mind-bending", "thriller"],
    },
    {
        "title": "The Dark Knight",
        "genre": ["Action", "Crime"],
        "language": "English",
        "rating": 9.0,
        "summary": "Batman faces the Joker in a fight for Gotham's soul.",
        "actors": ["Christian Bale", "Heath Ledger"],
        "mood": ["intense", "thriller"],
    },
    {
        "title": "Taare Zameen Par",
        "genre": ["Drama", "Family"],
        "language": "Hindi",
        "rating": 8.4,
        "summary": "A teacher helps a dyslexic child discover his creativity.",
        "actors": ["Aamir Khan"],
        "mood": ["emotional", "inspirational"],
    },
]


def actor_matches(movie: Dict[str, Any], actor_queries: List[str]) -> bool:
    if not actor_queries:
        return False
    movie_actors = movie.get("actors", [])
    for sel in actor_queries:
        for a in movie_actors:
            if sel.lower() in a.lower():
                return True
    return False


def recommend_movies(
    genre_filters: List[str],
    language_filters: List[str],
    mood_filter: str,
    min_rating: float,
    actor_queries: List[str],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for m in MOVIES:
        if genre_filters and not any(g.lower() == x.lower() for g in genre_filters for x in m["genre"]):
            continue
        if language_filters and m["language"].lower() not in [l.lower() for l in language_filters]:
            continue
        if mood_filter and not any(mood_filter.lower() in tag.lower() for tag in m.get("mood", [])):
            continue
        if m["rating"] < min_rating:
            continue
        # If actor queries provided, only include movies matching at least one selected actor
        if actor_queries:
            if actor_matches(m, actor_queries):
                results.append(m)
        else:
            results.append(m)

    # sort by rating desc
    results.sort(key=lambda x: x["rating"], reverse=True)

    # If enough strict matches (including actor when provided), return top 5
    if len(results) >= 3:
        return results[:5]

    # Not enough strict matches — build a prioritized pool to fill to at least 3.
    pool = MOVIES
    if language_filters:
        pool = [p for p in MOVIES if p["language"].lower() in [l.lower() for l in language_filters]]
        if not pool:
            pool = MOVIES
    pool = sorted(pool, key=lambda x: x["rating"], reverse=True)

    picked = results[:]

    # First try to add other movies that match the actor (if actor_queries provided)
    if actor_queries:
        actor_pool = [p for p in pool if actor_matches(p, actor_queries) and p not in picked]
        for p in actor_pool:
            picked.append(p)
            if len(picked) >= 3:
                break

    # Next, add movies that match genres (if provided)
    if len(picked) < 3 and genre_filters:
        genre_pool = [p for p in pool if any(g.lower() == x.lower() for g in genre_filters for x in p["genre"]) and p not in picked]
        for p in genre_pool:
            picked.append(p)
            if len(picked) >= 3:
                break

    # Next, add movies that match language (if provided)
    if len(picked) < 3 and language_filters:
        lang_pool = [p for p in pool if p["language"].lower() in [l.lower() for l in language_filters] and p not in picked]
        for p in lang_pool:
            picked.append(p)
            if len(picked) >= 3:
                break

    # Finally, fill from top-rated overall
    if len(picked) < 3:
        for p in pool:
            if p not in picked:
                picked.append(p)
            if len(picked) >= 3:
                break

    return picked[:5]


def main():
    st.title("Movie Recommendation Assistant")
    st.write("Recommend 3–5 movies based on genre, language, mood, rating or actors.")

    with st.sidebar.form(key="filters"):
        genres = st.multiselect("Genre", options=["Action", "Drama", "Comedy", "Thriller", "Sci-Fi", "Biography", "Music", "Crime", "Family", "Sport"], help="Pick one or more genres")
        languages = st.multiselect("Language", options=["Hindi", "Kannada", "English"], help="Pick languages to include")
        mood = st.text_input("Mood (one word)", help="e.g. inspirational, thriller, feel-good")
        min_rating = st.slider("Minimum IMDb rating", 0.0, 10.0, 6.0, 0.1)

        # Build actor options scoped to the selected languages (or all actors if none selected)
        def available_actors_for_languages(selected_languages: List[str]) -> List[str]:
            actors_set = set()
            langs = [l.lower() for l in selected_languages] if selected_languages else []
            for m in MOVIES:
                if langs and m["language"].lower() not in langs:
                    continue
                for a in m.get("actors", []):
                    actors_set.add(a)
            return sorted(actors_set)

        actor_options = available_actors_for_languages(languages)
        actor = st.multiselect("Actor (optional)", options=actor_options, help="Select one or more actors filtered by the selected languages")
        submit = st.form_submit_button("Recommend")

    if submit:
        recs = recommend_movies(genres, languages, mood, min_rating, actor)
        if not recs:
            st.info("No matches — showing popular picks.")
            recs = recommend_movies([], languages, "", 0.0, [])

        st.write("\n")
        for r in recs:
            st.markdown(f"**{r['title']}**  ")
            st.write(f"- Genre: {', '.join(r['genre'])}  \n- IMDb: {r['rating']}  \n- {r['summary']}")
            # If user requested an actor and this pick doesn't match, mark it as a fallback
            if actor:
                matches_actor = any(sel.lower() in a.lower() for sel in actor for a in r.get("actors", []))
                if not matches_actor:
                    st.caption("Suggested (does not match actor)")
            st.write("---")


if __name__ == '__main__':
    main()
