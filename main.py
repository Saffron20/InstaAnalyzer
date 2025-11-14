# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import numpy as np

# -----------------------------
# FASTAPI CONFIG
# -----------------------------
app = FastAPI(
    title="InstaAnalytics API",
    description="Backend API using real Instagram scraping",
    version="1.0.0"
)

# -----------------------------
# MODELS
# -----------------------------
class UserRequest(BaseModel):
    username: str
    count: int = 10

class CaptionRequest(BaseModel):
    caption: str

# -----------------------------
# CONSTANTS
# -----------------------------
RAPIDAPI_KEY = "8b026046dfmsh60caaa2176a6012p1ad1b5jsnd3afc89ad0e2"     # <<< REPLACE (use same key as app.py)
RAPID_HOST = "instagram-scraper-20251.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPID_HOST
}

# -----------------------------
# SCRAPER UTILITIES
# -----------------------------

def scrape_followers(username: str):
    url = f"https://{RAPID_HOST}/userinfo/?username_or_id={username}"
    r = requests.get(url, headers=HEADERS, timeout=10).json()
    return r.get("data", {}).get("follower_count", 0)

def scrape_posts(username: str, count: int):
    url = f"https://{RAPID_HOST}/userposts/?username_or_id={username}&count={count}"
    r = requests.get(url, headers=HEADERS, timeout=10).json()
    return r.get("data", {}).get("items", []) or []

def compute_engagement(post, followers):
    likes = int(post.get("like_count", 0) or 0)
    views = int(post.get("view_count") or post.get("play_count") or post.get("video_view_count") or 0)
    if views > 0:
        return likes / views
    if followers > 0:
        return likes / followers
    return 0


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
def root():
    return {"message": "🚀 InstaAnalytics API is running!"}



# 1️⃣ ANALYZE USER (REAL DATA)
@app.post("/analyze")
def analyze_user(data: UserRequest):
    u = data.username
    followers = scrape_followers(u)
    posts = scrape_posts(u, data.count)

    engagements = [compute_engagement(p, followers) for p in posts]

    result = {
        "username": u,
        "followers": followers,
        "posts_analyzed": len(posts),
        "avg_engagement": round(float(np.mean(engagements)) if engagements else 0, 4)
    }
    return result



# 2️⃣ SENTIMENT ANALYSIS (REAL LOGIC)
@app.post("/sentiment")
def sentiment_analysis(caption: CaptionRequest):

    text = caption.caption.lower()

    positive_keywords = ["love", "amazing", "great", "beautiful", "happy"]
    negative_keywords = ["hate", "bad", "worst", "angry", "sad"]

    score = 0
    for w in positive_keywords:
        if w in text:
            score += 1
    for w in negative_keywords:
        if w in text:
            score -= 1

    sentiment = "neutral"
    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"

    return {
        "caption": caption.caption,
        "sentiment": sentiment,
        "score": score
    }



# 3️⃣ TOP POSTS
@app.post("/top_posts")
def top_posts(data: UserRequest):
    posts = scrape_posts(data.username, data.count)

    formatted_posts = []
    for p in posts:
        formatted_posts.append({
            "id": p.get("id"),
            "likes": int(p.get("like_count", 0) or 0),
            "comments": int(p.get("comment_count", 0) or 0),
            "views": int(p.get("view_count") or p.get("play_count") or 0),
        })

    # sort by likes
    top = sorted(formatted_posts, key=lambda x: x["likes"], reverse=True)[:3]

    return {"username": data.username, "top_posts": top}



# 4️⃣ HASHTAG SUGGESTION (REAL LOGIC BASED ON CAPTIONS)
@app.post("/hashtag_suggest")
def hashtag_suggest(data: UserRequest):

    posts = scrape_posts(data.username, data.count)

    all_hashtags = []
    for p in posts:
        cap = ""
        if isinstance(p.get("caption"), dict):
            cap = p["caption"].get("text", "")
        elif isinstance(p.get("caption"), str):
            cap = p["caption"]

        if cap:
            tags = [t.lower() for t in cap.split() if t.startswith("#")]
            all_hashtags.extend(tags)

    # frequency-based suggestions
    freq = {}
    for t in all_hashtags:
        freq[t] = freq.get(t, 0) + 1

    top_tags = sorted(freq, key=freq.get, reverse=True)[:10]

    return {
        "username": data.username,
        "recommended_hashtags": top_tags or ["#instagram", "#trending"]
    }



# 5️⃣ GROWTH PREDICTION (REAL BASIC LOGIC)
@app.post("/predict_growth")
def growth_predict(data: UserRequest):

    followers = scrape_followers(data.username)

    # simple ML-like logic: +2.5% growth
    prediction = int(followers * 1.025)

    return {
        "username": data.username,
        "current_followers": followers,
        "predicted_followers_next_week": prediction,
        "growth_rate": "2.5%"
    }
