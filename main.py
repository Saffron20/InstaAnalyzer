# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="InstaAnalytics API",
    description="Backend API for Instagram analysis and forecasting",
    version="1.0.0"
)

class UserRequest(BaseModel):
    username: str

@app.get("/")
def root():
    return {"message": "🚀 InstaAnalytics API is running!"}

@app.post("/analyze")
@app.post("/analyze")
def analyze_user(data: UserRequest):
    user = data.username
    # call your scraping logic here
    results = {"followers": 12000, "engagement": 4.5}
    return {"user": user, "analysis": results}

# uvicorn main:app --reload --host 0.0.0.0 --port 8000
