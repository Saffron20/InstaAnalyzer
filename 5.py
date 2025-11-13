import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from io import BytesIO
import requests
 
st.set_page_config(page_title="📈 Engagement Forecast", layout="wide")
st.markdown('<div style="font-size:28px;font-weight:800;background:linear-gradient(90deg,#ff6ec4,#7873f5);-webkit-background-clip:text;-webkit-text-fill-color:transparent">📈 Engagement Forecast & Trend Prediction</div>', unsafe_allow_html=True)
 
API_KEY = st.secrets.get("RAPIDAPI_KEY")
if not API_KEY:
    st.error("RAPIDAPI_KEY not found. Add to .streamlit/secrets.toml")
    st.stop()
 
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "instagram-scraper-20251.p.rapidapi.com"
}
 
username = st.text_input("Enter an Instagram username for forecasting", "nike")
limit = st.number_input("Number of posts to analyze", 10, 50, 20)
 
if st.button("🔮 Forecast Engagement"):
    with st.spinner("Fetching posts and building model..."):
        url = f"https://instagram-scraper-20251.p.rapidapi.com/userposts/?username_or_id={username}&count={limit}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            data = response.json()
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            st.stop()
 
        posts = data.get("data", {}).get("items", []) or []
        if not posts:
            st.error("No posts found for this account.")
            st.stop()
 
        df = pd.DataFrame([{
            "taken_at": p.get("taken_at"),
            "likes": int(p.get("like_count", 0) or 0),
            "views": int(p.get("view_count") or p.get("play_count") or p.get("video_view_count") or 0)
        } for p in posts])
 
        df["taken_at"] = pd.to_datetime(df["taken_at"], unit="s", errors="coerce")
        df = df.sort_values("taken_at").reset_index(drop=True)
        df["eng_score"] = (df["likes"] / df["views"].replace(0, np.nan)).fillna(0)
        df["post_index"] = np.arange(len(df))
 
        if len(df) < 3:
            st.info("Not enough posts to build a reliable forecast (need at least 3).")
            st.stop()
 
        X = df[["post_index"]].values
        y = df["eng_score"].values
        model = LinearRegression().fit(X, y)
        df["predicted"] = model.predict(X)
 
        # Future 5 posts prediction
        future_idx = np.arange(len(df), len(df) + 5)
        future_preds = model.predict(future_idx.reshape(-1, 1))
        last_date = df["taken_at"].max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=5, freq="D")
        df_future = pd.DataFrame({"post_index": future_idx, "predicted": future_preds, "taken_at": future_dates})
 
        # Plot
        fig = px.line(df, x="taken_at", y="eng_score", markers=True, title=f"Engagement Forecast for @{username}")
        fig.add_scatter(x=df["taken_at"], y=df["predicted"], mode='lines', name="Fitted (predicted)", line=dict(dash='dash'))
        fig.add_scatter(x=df_future["taken_at"], y=df_future["predicted"], mode='lines+markers', name="Future Forecast", line=dict(color='orange'))
        fig.update_layout(yaxis_title="Engagement Score", xaxis_title="Post Date")
        st.plotly_chart(fig, use_container_width=True)
 
        # Metrics
        r2 = r2_score(y, df["predicted"])
        mae = mean_absolute_error(y, df["predicted"])
        st.metric("Model R² Score", f"{r2:.3f}")
        st.metric("Mean Absolute Error", f"{mae:.3f}")
 
        # Download
        out = BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="historical", index=False)
            df_future.to_excel(writer, sheet_name="forecast", index=False)
        st.download_button("⬇ Download Forecast Data", data=out.getvalue(), file_name=f"{username}_forecast.xlsx")
        st.success("Forecast completed.")
 
 
