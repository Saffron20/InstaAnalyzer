import streamlit as st
import pandas as pd
import requests
import os
from io import BytesIO
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.express as px

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(page_title="InstAnalytics - FREE+", layout="wide")
st.markdown("""
<style>
.bigheader {
  font-size: 38px;
  font-weight: 900;
  background: linear-gradient(90deg, #ff6ec4, #7873f5);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom:15px;
}
.section-title {
  font-size:22px;
  font-weight:700;
  margin-top:25px;
  padding-bottom:4px;
  border-bottom:2px solid #ff6ec4;
}
.metric-card {
  background: linear-gradient(135deg, #ff6ec4, #7873f5);
  color: white;
  border-radius:12px;
  padding:10px 15px;
  text-align:center;
  font-weight:bold;
  margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="bigheader">🚀 AI-Enhanced Instagram Intelligence</div>', unsafe_allow_html=True)

# ==========================
# INPUTS
# ==========================
API_KEY = os.environ.get("RAPIDAPI_KEY")

if not API_KEY:
    st.error('RAPIDAPI_KEY not set! Run in PowerShell:  $env:RAPIDAPI_KEY="xxxxxxxx" ')
    st.stop()

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "instagram-scraper-20251.p.rapidapi.com"
}

usernames = st.text_input("IG usernames (comma)", "nike, puma")
limit = st.number_input("Posts per account", 1, 50, 10)

# ==========================
# ANALYSIS BUTTON
# ==========================
if st.button("Analyze"):
    names = [u.strip() for u in usernames.split(",")]

    all_posts = []
    followers_list = []

    with st.spinner("✨ Scraping Instagram data..."):
        for u in names:
            # Followers
            f_url = f"https://instagram-scraper-20251.p.rapidapi.com/userinfo/?username_or_id={u}"
            fr = requests.get(f_url, headers=headers).json()
            followers = fr.get("data", {}).get("follower_count", None)
            followers_list.append({"username": u, "followers": followers})

            # Posts
            p_url = f"https://instagram-scraper-20251.p.rapidapi.com/userposts/?username_or_id={u}&count={limit}"
            pr = requests.get(p_url, headers=headers).json()
            posts = pr.get("data", {}).get("items", [])

            for post in posts:
                likes = post.get("like_count", 0)
                views = (
                    post.get("view_count")
                    or post.get("play_count")
                    or post.get("video_view_count")
                    or 0
                )
                ts = post.get("taken_at", None)
                cap = post.get("caption", {}).get("text") if isinstance(post.get("caption"), dict) else ""

                all_posts.append({
                    "username": u,
                    "likes": likes,
                    "views": views,
                    "caption": cap,
                    "eng_score": likes / views if views else None,
                    "taken_at": ts
                })

    df = pd.DataFrame(all_posts)
    df_f = pd.DataFrame(followers_list)

    if df.empty:
        st.error("❌ No posts returned")
        st.stop()

    df["taken_at"] = pd.to_datetime(df["taken_at"], unit="s", errors="coerce")
    df["hour"] = df["taken_at"].dt.hour

    # ==========================
    # KPI METRICS ROW
    # ==========================
    avg_eng = round(df["eng_score"].mean(), 3)
    total_followers = df_f["followers"].sum()
    best_hour = df.groupby("hour")["likes"].mean().idxmax()

    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="metric-card">⭐ Avg Engagement: {avg_eng}</div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card">👥 Total Followers: {total_followers:,}</div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card">⏰ Best Hour: {best_hour}:00</div>', unsafe_allow_html=True)

    # ==========================
    # NEW FEATURES
    # ==========================
    # Virality Predictor
    tmp = df.dropna(subset=["likes","views"])
    if len(tmp)>2:
        X = tmp[["views"]].values
        y = tmp["likes"].values
        model = LinearRegression().fit(X,y)
        pred_views = st.number_input("Enter expected views for prediction", 1000, 10_000_000, 50000)
        pred_likes = model.predict(np.array([[pred_views]]))[0]

    # Heatmap
    df["weekday"] = df["taken_at"].dt.day_name()
    pivot = df.pivot_table(values="eng_score", index="weekday", columns="hour", aggfunc="mean")

    # Competitor overlap
    overlap = 0
    if len(df_f)>=2:
        f = df_f["followers"].values
        overlap = min(f)/max(f)*100 if max(f)>0 else 0

    # Hook Score
    df["caption"] = df["caption"].fillna("")
    df["first_line_len"] = df["caption"].str.split("\n").str[0].str.len()
    df["hook_score"] = df["eng_score"] * (df["first_line_len"] / max(df["first_line_len"].max(),1))

    # ==========================
    # TABS FOR INTERACTIVE DISPLAY
    # ==========================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Summary","Virality","Heatmap","Overlap","Hook","Raw Data"])

    # ---------- SUMMARY TAB ----------
    with tab1:
        st.subheader("Brand Comparison — Engagement Score Avg")
        avg_eng_df = df.groupby("username")["eng_score"].mean().reset_index()
        fig1 = px.bar(avg_eng_df, x="username", y="eng_score",
                      text="eng_score",
                      color="eng_score",
                      color_continuous_scale=px.colors.sequential.Plasma,
                      labels={"eng_score":"Engagement Score"},
                      title="🌟 Avg Engagement Score per Brand")
        fig1.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig1.update_layout(yaxis=dict(range=[0, max(avg_eng_df["eng_score"])*1.2]))
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Followers per Brand")
        fig_followers = px.bar(df_f, x="username", y="followers",
                               color="followers",
                               text="followers",
                               color_continuous_scale=px.colors.sequential.Viridis,
                               title="👥 Followers per Brand")
        fig_followers.update_traces(texttemplate="%{text}", textposition="outside")
        st.plotly_chart(fig_followers, use_container_width=True)

        st.success(f"🔥 Best posting hour: {best_hour}:00")

    # ---------- VIRALITY TAB ----------
    with tab2:
        st.subheader("Reel Virality Predictor")
        st.write(f"💥 Predicted Likes for {pred_views:,} views: **{int(pred_likes):,}**")

    # ---------- HEATMAP TAB ----------
    with tab3:
        st.subheader("Engagement Heatmap (Day x Hour)")
        pivot_reset = pivot.reset_index().melt(id_vars="weekday", var_name="hour", value_name="eng_score")
        fig3 = px.density_heatmap(pivot_reset, x="hour", y="weekday", z="eng_score",
                                  color_continuous_scale='Inferno',
                                  text_auto=".2f",
                                  labels={"eng_score":"Engagement Score"})
        fig3.update_layout(title="🌈 Engagement Heatmap",
                           yaxis={'categoryorder':'array',
                                  'categoryarray':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']})
        st.plotly_chart(fig3, use_container_width=True)

    # ---------- OVERLAP TAB ----------
    with tab4:
        st.subheader("Competitor Overlap %")
        st.write(f"🤝 Approx Overlap: **{overlap:0.1f}%**")

    # ---------- HOOK TAB ----------
    with tab5:
        st.subheader("Hook Score — 1st Line Effect")
        hook_df = df.groupby("username")["hook_score"].mean().reset_index()
        fig2 = px.bar(hook_df, x="username", y="hook_score",
                      text="hook_score",
                      color="hook_score",
                      color_continuous_scale=px.colors.sequential.Viridis,
                      title="🔥 Hook Score by Brand")
        fig2.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------- RAW DATA TAB ----------
    with tab6:
        st.subheader("Raw Posts Data (first 50)")
        st.dataframe(df.head(50))

    # ==========================
    # EXPORT EXCEL
    # ==========================
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="posts", index=False)
        df_f.to_excel(writer, sheet_name="followers", index=False)
    st.download_button("⬇ Export Excel", data=out.getvalue(), file_name="insta_results.xlsx")

    # ==========================
    # CELEBRATE
    # ==========================
    st.balloons()