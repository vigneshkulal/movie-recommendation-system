"""Content-based movie recommender (TF-IDF + cosine similarity)."""
import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TOP_N = 5


def _clean(value):
    """Return a lowercase string, or '' for missing values."""
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def _genre_list(value):
    if pd.isna(value) or not str(value).strip():
        return []
    return [g.strip().lower() for g in str(value).split(",") if g.strip()]


class MovieRecommender:
    def __init__(self, df):
        df = df.copy()
        for col in ("genres", "description", "year"):
            if col not in df.columns:
                df[col] = np.nan
        df = df.dropna(subset=["title"])
        df["title"] = df["title"].astype(str).str.strip()
        df = df[df["title"] != ""]

        # Duplicate strategy:
        #  1. rows with the same title AND same metadata are exact duplicates -> keep the first
        #  2. rows with the same title but different metadata are different movies
        #     -> keep both and label them "Title (year)" (or "Title (id N)" if no year)
        df["_key"] = df["title"].str.lower()
        df = df.drop_duplicates(subset=["_key", "genres", "description"], keep="first")
        dup = df["_key"].duplicated(keep=False)
        df["label"] = df["title"]
        for i in df[dup].index:
            year = df.at[i, "year"]
            if pd.notna(year):
                df.at[i, "label"] = f"{df.at[i, 'title']} ({int(year)})"
            else:
                df.at[i, "label"] = f"{df.at[i, 'title']} (id {df.at[i, 'movie_id']})"

        df = df.reset_index(drop=True)
        self.df = df
        self.genres = df["genres"].apply(_genre_list)

        # "Sci-Fi" -> "scifi" so it stays a single token; description words are added after
        genre_text = self.genres.apply(lambda gs: " ".join(re.sub(r"[^a-z]", "", g) for g in gs))
        desc_text = df["description"].apply(_clean)
        df["text"] = (genre_text + " " + genre_text + " " + desc_text).str.strip()
        self.has_data = df["text"] != ""

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(df["text"].where(self.has_data, "empty"))
        self.terms = np.array(self.vectorizer.get_feature_names_out())

    def titles(self):
        return sorted(self.df["label"].tolist())

    def _find(self, name):
        name = _clean(name)
        exact = self.df.index[self.df["label"].str.lower() == name]
        if len(exact):
            return exact[0], None
        same_title = self.df.index[self.df["title"].str.lower() == name]
        if len(same_title):
            return same_title[0], None
        return None, None

    def _explain(self, i, j):
        shared = [g for g in self.genres[i] if g in self.genres[j]]
        parts = []
        if shared:
            parts.append("shared genres: " + ", ".join(g.title() for g in shared))
        prod = self.matrix[i].multiply(self.matrix[j]).toarray().ravel()
        words = [t for t in self.terms[np.argsort(prod)[::-1][:3]]
                 if prod[list(self.terms).index(t)] > 0 and t not in {re.sub(r"[^a-z]", "", g) for g in shared}]
        if words:
            parts.append("common keywords: " + ", ".join(words))
        return "; ".join(parts) if parts else "no shared genres or keywords (weak match)"

    def recommend(self, name, n=TOP_N):
        """Returns dict: status ('ok' | 'not_found' | 'no_metadata'), message, results (DataFrame)."""
        empty = pd.DataFrame(columns=["rank", "title", "score", "why"])
        if not name or not str(name).strip():
            return {"status": "not_found", "message": "Please enter a movie title.", "results": empty}

        idx, _ = self._find(name)
        if idx is None:
            return {"status": "not_found",
                    "message": f"Movie '{name}' was not found in the dataset.", "results": empty}
        if not self.has_data[idx]:
            return {"status": "no_metadata",
                    "message": f"'{self.df.at[idx, 'label']}' has no genres or description, "
                               "so similar movies cannot be calculated.",
                    "results": empty}

        scores = cosine_similarity(self.matrix[idx], self.matrix).ravel()
        order = [j for j in np.argsort(-scores, kind="stable")
                 if j != idx and self.has_data[j]
                 and self.df.at[j, "title"].lower() != self.df.at[idx, "title"].lower()]
        order = order[:n]

        rows = [{"rank": r + 1, "title": self.df.at[j, "label"], "score": round(float(scores[j]), 3),
                 "why": self._explain(idx, j)} for r, j in enumerate(order)]
        msg = f"Top {len(rows)} movies similar to '{self.df.at[idx, 'label']}'"
        if len(rows) < n:
            msg += f" (only {len(rows)} valid movies available)"
        return {"status": "ok", "message": msg, "results": pd.DataFrame(rows, columns=empty.columns)}


def load(path):
    return MovieRecommender(pd.read_csv(path))


if __name__ == "__main__":
    import sys
    rec = load("data/movies.csv")
    result = rec.recommend(" ".join(sys.argv[1:]) or "Space Journey")
    print(result["message"])
    print(result["results"].to_string(index=False))
