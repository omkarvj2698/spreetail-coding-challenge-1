from fastapi import FastAPI, Request
from typing import List, Tuple
import time, os
import openai

app = FastAPI(title="Review Analytics API", description="Classify reviews and summarize tags using real OpenAI tagging with fallback mock.")

# In-memory store
reviews_db = []  # Each entry: {"text": str, "tags": List[str], "processing_time": float}


def get_ai_tags(review_text: str) -> List[str]:
    """
    AI tagging with a real OpenAI API call and safe mock fallback.
    Set your OpenAI API key in the environment variable OPENAI_API_KEY.
    """
    prompt = f"""
    You are an AI assistant. Read the following customer review and generate up to 3 relevant tags.

    Review: "{review_text}"

    Respond strictly with a JSON array of concise lowercase tags.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            ai_output = response.choices[0].message.content.strip()
            print("[OPENAI RAW OUTPUT]", ai_output)

            # Parse safely (expecting a JSON-like list)
            tags = [t.strip().strip('"').strip("'") for t in ai_output.replace('[', '').replace(']', '').split(',') if t.strip()]
            return tags[:3]

        except Exception as e:
            print(f"[OpenAI Error] {e}, falling back to mock tags.")

    # --- Fallback mock logic ---
    lower_text = review_text.lower()
    if "late" in lower_text or "delay" in lower_text:
        return ["late_delivery", "shipping_delay"]
    elif "broken" in lower_text or "not working" in lower_text:
        return ["defective_item", "product_failure"]
    elif "refund" in lower_text or "return" in lower_text:
        return ["refund_request", "customer_service"]
    else:
        return ["general_feedback"]


def top_k_tags(tag_list: List[str], k: int) -> List[Tuple[str, int]]:
    freq = {}
    for tag in tag_list:
        freq[tag] = freq.get(tag, 0) + 1
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:k]


@app.post("/analyze")
async def analyze_review(request: Request):
    payload = await request.json()
    review_text = payload.get("review_text", "").strip()

    if not review_text:
        return {"error": "Missing review_text"}

    start_time = time.time()
    tags = get_ai_tags(review_text)
    elapsed = round(time.time() - start_time, 3)

    reviews_db.append({"text": review_text, "tags": tags, "processing_time": elapsed})
    print(f"[INFO] Review processed in {elapsed}s -> Tags: {tags}")

    return {"review_text": review_text, "tags": tags, "processing_time": elapsed}


@app.get("/summary")
async def get_summary():
    if not reviews_db:
        return {"message": "No reviews analyzed yet."}

    all_tags = [tag for entry in reviews_db for tag in entry["tags"]]
    total_reviews = len(reviews_db)
    avg_processing_time = round(sum(r["processing_time"] for r in reviews_db) / total_reviews, 2)
    top_tags = top_k_tags(all_tags, 3)

    return {
        "total_reviews": total_reviews,
        "top_tags": top_tags,
        "avg_processing_time": avg_processing_time
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)