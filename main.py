# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="InstaAnalytics API",
    description="Backend API for Instagram analysis and forecasting",
    version="1.0.0"
)

# -----------------------------
# MODELS
# -----------------------------
class UserRequest(BaseModel):
    username: str

class CaptionRequest(BaseModel):
    caption: str

# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
def root():
    return {"message": "🚀 InstaAnalytics API is running!"}


# 1️⃣ ANALYZE USER
@app.post("/analyze")
def analyze_user(data: UserRequest):
    user = data.username
    results = {
        "followers": 12000,
        "engagement": 4.5,
        "posts": 56
    }
    return {"user": user, "analysis": results}


# 2️⃣ SENTIMENT ANALYSIS
@app.post("/sentiment")
def sentiment_analysis(caption: CaptionRequest):
    # Dummy sentiment logic
    if "love" in caption.caption.lower():
        sentiment = "positive"
    elif "hate" in caption.caption.lower():
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "caption": caption.caption,
        "sentiment": sentiment,
        "score": 0.75
    }


# 3️⃣ TOP POSTS
@app.post("/top_posts")
def top_posts(data: UserRequest):
    return {
        "user": data.username,
        "top_posts": [
            {"id": "1", "likes": 3400, "comments": 120},
            {"id": "2", "likes": 2890, "comments": 95},
            {"id": "3", "likes": 2500, "comments": 80}
        ]
    }


# 4️⃣ HASHTAG SUGGESTION
@app.post("/hashtag_suggest")
def hashtag_suggest(data: UserRequest):
    return {
        "user": data.username,
        "recommended_hashtags": [
            "#trending", "#viral", "#explorepage",
            "#fyp", "#motivation", "#fashion"
        ]
    }


# 5️⃣ GROWTH PREDICTION (Dummy ML)
@app.post("/predict_growth")
def growth_predict(data: UserRequest):
    return {
        "user": data.username,
        "predicted_followers_next_week": 12480,
        "growth_rate": "3.8%"
    }


# 6️⃣ ACCOUNT HEALTH SCORE
@app.post("/health_score")
def account_health(data: UserRequest):
    score = 84
    category = "Good" if score >= 70 else "Average"

    return {
        "user": data.username,
        "health_score": score,
        "category": category
    }


# uvicorn main:app --reload --host 0.0.0.0 --port 8000
