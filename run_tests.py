"""Runs TC1-TC6 from the problem statement and writes results/test_results.txt"""
import os
import sys

import pandas as pd

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base)
from recommender import MovieRecommender, load

test_df = pd.read_csv(os.path.join(base, "data", "test_movies.csv"))
lines = []


def check(name, input_desc, expected, res, passed):
    lines.append(f"{name} | Input: {input_desc}")
    lines.append(f"  Expected: {expected}")
    lines.append(f"  Status: {res['status']} | {res['message']}")
    if len(res["results"]):
        lines.append(res["results"].to_string(index=False))
    lines.append(f"  Result: {'PASS' if passed else 'FAIL'}\n")
    return passed


rec = MovieRecommender(test_df)
all_ok = []

r = rec.recommend("Space Journey")
top = r["results"]["title"].tolist()
all_ok.append(check("TC1", "Space Journey", "other movies, Sci-Fi/Adventure ranked first", r,
                    "Space Journey" not in top and set(top[:2]) == {"Galactic Mission", "Robot Planet"}))

r = rec.recommend("Funny Neighbours")
all_ok.append(check("TC2", "Funny Neighbours", "recommendations without Funny Neighbours", r,
                    len(r["results"]) > 0 and "Funny Neighbours" not in r["results"]["title"].tolist()))

r = rec.recommend("Some Random Movie")
all_ok.append(check("TC3", "Some Random Movie", "clear not-found message", r, r["status"] == "not_found"))

missing = pd.concat([test_df, pd.DataFrame([{"movie_id": 6, "title": "No Genre Film", "genres": None}])],
                    ignore_index=True)
rec_m = MovieRecommender(missing)
r = rec_m.recommend("No Genre Film")
ok = r["status"] == "no_metadata"
r2 = rec_m.recommend("Space Journey")
ok = ok and "No Genre Film" not in r2["results"]["title"].tolist()
all_ok.append(check("TC4", "No Genre Film (missing genres)", "handled gracefully, no crash", r, ok))

r = rec.recommend("Ocean Mystery")
all_ok.append(check("TC5", "Ocean Mystery (only 4 other movies in dataset)",
                    "return only available recommendations, not padded to 5", r, len(r["results"]) == 4))

dup = pd.concat([test_df, pd.DataFrame([
    {"movie_id": 6, "title": "Space Journey", "genres": "Sci-Fi, Adventure"},   # exact duplicate
    {"movie_id": 7, "title": "Robot Planet", "genres": "Sci-Fi, Family"}])],    # same title, different movie
    ignore_index=True)
rec_d = MovieRecommender(dup)
r = rec_d.recommend("Space Journey")
titles = r["results"]["title"].tolist()
all_ok.append(check("TC6", "Space Journey (dataset has duplicate titles)",
                    "exact duplicates removed, same-title movies disambiguated", r,
                    "Space Journey" not in titles and len(set(titles)) == len(titles)
                    and sum("Robot Planet" in t for t in rec_d.titles()) == 2))

lines.append("--- Full dataset sample (data/movies.csv) ---")
full = load(os.path.join(base, "data", "movies.csv"))
for t in ["Space Journey", "Funny Neighbours", "Mystery Movie"]:
    res = full.recommend(t)
    lines.append(f"\n{res['message']}")
    if len(res["results"]):
        lines.append(res["results"].to_string(index=False))

lines.append(f"\nSummary: {sum(all_ok)}/{len(all_ok)} test cases passed")
out = "\n".join(lines)
print(out)
with open(os.path.join(base, "results", "test_results.txt"), "w") as f:
    f.write(out)
