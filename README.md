# Movie Recommendation System

Content-based movie recommender. The user picks a movie and gets five similar movies,
each with a short reason why it was recommended.

## How it works
1. Load `data/movies.csv` (movie_id, title, year, genres, description).
2. Preprocess: lowercase, strip extra spaces, fill missing values with empty text,
   turn genres like "Sci-Fi" into single tokens ("scifi"). Genres are repeated twice
   so they weigh more than description words.
3. Convert the text to TF-IDF vectors (scikit-learn `TfidfVectorizer`, English stop words removed).
4. Compute cosine similarity between the selected movie and all others.
5. Return the top 5, excluding the selected movie.
6. Explanation = shared genres + top common keywords for each recommendation.

## Edge cases
| Case | Behaviour |
|---|---|
| Unknown title | Returns "No results" |
| Selected movie has no genres/description | Returns a message that similarity cannot be calculated |
| Other movies with no metadata | Skipped from recommendations |
| Fewer than 5 other movies | Returns only what is available (not padded) |
| Duplicate titles | Exact duplicates (same title + same metadata) are removed, keeping the first. Same title but different metadata = different movies, shown as `Title (year)`, or `Title (id N)` if no year |
| Zero similarity | Still listed (if needed to fill the list) but marked "weak match" |

## Quick Start Guide (For Reviewers)

### Prerequisites
- Python 3.8 or higher installed on your system.

---

### Step 1: Install Required Packages
Open your terminal (PowerShell, Command Prompt, or Bash) in this project directory and run:
```bash
pip install -r requirements.txt
```

---

### Step 2: Run the Web Application
Start the Streamlit web dashboard:
```bash
python -m streamlit run app.py
```
*(Alternatively, you can also run `streamlit run app.py` if Streamlit is in your system PATH).*

---

### Step 3: Open the Web Application
Once launched, the app will automatically open in your default browser. If it doesn't open automatically, navigate to:
-> **[http://localhost:8501](http://localhost:8501)**

> **Note / Troubleshooting:**
> - To **stop** the application: Press `Ctrl + C` in the terminal.
> - If port 8501 is already in use by another app, you can launch on port 8502:
>   ```bash
>   python -m streamlit run app.py --server.port 8502
>   ```

---

## Alternative Run Options

### Command-Line (CLI) Mode:
Run recommendations directly in the console without the UI:
```bash
python recommender.py "Space Journey"
```

### Automated Test Suite:
Run test cases TC1–TC6 (validates edge cases and writes to `results/test_results.txt`):
```bash
python tests/run_tests.py
```

## Files
- `recommender.py` - recommendation engine
- `app.py` - Streamlit dashboard
- `requirements.txt` - required Python libraries
- `background.jpg` - UI background styling asset
- `.streamlit/config.toml` - Streamlit server & port configuration
- `data/movies.csv` - synthetic dataset (41 rows, includes duplicates and missing metadata)
- `data/test_movies.csv` - the 5-movie test dataset from the problem statement
- `tests/run_tests.py` - TC1-TC6 automated test suite
- `results/test_results.txt` - output from the test run (6/6 passed)

## Sample output
```
Top 5 movies similar to 'Space Journey'
 rank              title  score  why
    1       Star Voyager  0.422  shared genres: Sci-Fi, Adventure; common keywords: galaxy
    2 Robot Planet (2020) 0.347  shared genres: Sci-Fi, Adventure
    3   Galactic Mission  0.295  shared genres: Sci-Fi, Adventure
    4    Mountain Escape  0.167  shared genres: Adventure
    5     Alien Frontier  0.162  shared genres: Sci-Fi
```
