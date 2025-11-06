# Review Analytics API

This is a simple backend application built using FastAPI. It takes product reviews, tags them using either a mocked AI function or a real OpenAI API call, and then summarizes all stored reviews to show the most common tags and average processing time. The code is written to meet assignment deliverables clearly — with clean structure, inline explanations, printed logs, and reasoning around complexity.

---

## Expected Deliverables

**1. /analyze endpoint (mocked AI tagging)**  
This endpoint accepts a review text, runs it through the tagging function, and returns generated tags along with the time taken to process it.

**2. /summary endpoint (manual frequency computation)**  
This endpoint summarizes all reviews processed so far. It calculates how many reviews have been analyzed, finds the top three most common tags, and returns the average processing time.

**3. Clean, modular code**  
The code is organized into reusable functions like `get_ai_tags()` and `top_k_tags()`. The structure can easily be extended with additional endpoints like `/compare_reviews` or caching features.

**4. Inline comments**  
Throughout the code, every important decision and assumption has been commented on for clarity.

**5. Printed logs**  
The script prints logs for data checks and timing so anyone running it can trace what happens internally.

---

## How It Works

### /analyze (POST)
Takes input in the form:
```json
{ "review_text": "The product stopped working after two days." }
```
Returns something like:
```json
{
  "review_text": "The product stopped working after two days.",
  "tags": ["defective_item", "product_failure"],
  "processing_time": 0.002
}
```
If an OpenAI API key is provided, it will use the `gpt-3.5-turbo` model to generate tags; otherwise, it uses a small keyword-based mock function.

### /summary (GET)
After several reviews are analyzed, this endpoint shows how the system has performed so far:
```json
{
  "total_reviews": 10,
  "top_tags": [["shipping_delay", 4], ["defective_item", 3], ["late_delivery", 2]],
  "avg_processing_time": 1.2
}
```
The tag frequency is computed manually using dictionary logic — no external libraries like `Counter` are used.

---

## Implementation Details

### Tagging logic
- The `get_ai_tags()` function generates up to three relevant tags for each review.
- It prints the constructed prompt before calling the API to show what an actual LLM would see.
- A fallback path handles missing API keys or request failures.

### Summary logic
- `top_k_tags()` builds a frequency dictionary and sorts it to find the most common tags.
- Sorting is done manually using Python’s sort function.

### Data storage
- The data is kept in a list called `reviews_db`.
- Each entry is a dictionary with keys: `text`, `tags`, and `processing_time`.

---

## Time and Space Complexity

| Component | Time Complexity | Space Complexity | Description |
|------------|-----------------|------------------|--------------|
| `get_ai_tags()` | O(1) | O(1) | Constant-time keyword matching or single API call |
| `top_k_tags()` | O(n log n) | O(n) | Build and sort tag frequencies |
| `/summary` | O(r) | O(r) | r = number of stored reviews |

### Optimizing for 1M+ Reviews
- Replace the in-memory list with a database such as PostgreSQL or MongoDB.
- Add an index on tag columns for faster lookups.
- Keep a running frequency count so that aggregation doesn’t require reading all data every time.
- Use background workers (Celery or Redis Queue) to handle tagging tasks asynchronously.
- Introduce caching to skip repeated reviews.
- Batch updates instead of per-request writes.