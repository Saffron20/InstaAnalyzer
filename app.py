import streamlit as st
import pandas as pd
import requests
import os
from io import BytesIO
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="InstAnalytics - FREE+",
    layout="wide",
    initial_sidebar_state="expanded"
)
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

# Use Streamlit secrets for API key
API_KEY = st.secrets.get("RAPIDAPI_KEY")
if not API_KEY:
    st.error('RAPIDAPI_KEY not set! Add it to .streamlit/secrets.toml or Streamlit Cloud secrets.')
    st.stop()

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "instagram-scraper-20251.p.rapidapi.com"
}

usernames = st.text_input("IG usernames (comma)", "nike, puma")
limit = st.number_input("Posts per account", 1, 50, 10)

if st.button("Analyze"):
    names = [u.strip() for u in usernames.split(",") if u.strip()]
    if not names:
        st.error("Please enter at least one username.")
        st.stop()

    all_posts = []
    followers_list = []

    with st.spinner("✨ Scraping Instagram data..."):
        for u in names:
            # Followers
            f_url = f"https://instagram-scraper-20251.p.rapidapi.com/userinfo/?username_or_id={u}"
            try:
                fr = requests.get(f_url, headers=headers, timeout=15).json()
            except Exception as e:
                st.error(f"Request error for user {u}: {e}")
                st.stop()

            followers = fr.get("data", {}).get("follower_count", None)
            followers_list.append({
                "username": u,
                "followers": int(followers) if followers is not None else None
            })

            # Posts
            p_url = f"https://instagram-scraper-20251.p.rapidapi.com/userposts/?username_or_id={u}&count={limit}"
            try:
                pr = requests.get(p_url, headers=headers, timeout=15).json()
            except Exception as e:
                st.error(f"Request error for posts of {u}: {e}")
                st.stop()

            posts = pr.get("data", {}).get("items", []) or []

            for post in posts:
                likes = int(post.get("like_count", 0) or 0)
                views = int(post.get("view_count") or post.get("play_count") or post.get("video_view_count") or 0)
                ts = post.get("taken_at", None)
                cap = ""
                caption_field = post.get("caption", "")
                if isinstance(caption_field, dict):
                    cap = caption_field.get("text", "") or ""
                elif isinstance(caption_field, str):
                    cap = caption_field

                all_posts.append({
                    "username": u,
                    "likes": likes,
                    "views": views,
                    "comments": int(post.get("comment_count", 0) or 0),
                    "caption": cap,
                    "eng_score": (likes / views) if views else (likes / max(1, followers) if followers else None),
                    "taken_at": ts
                })

    df = pd.DataFrame(all_posts)
    df_f = pd.DataFrame(followers_list)

    if df.empty:
        st.error("❌ No posts returned")
        st.stop()

    # Parse times and features
    df["taken_at"] = pd.to_datetime(df["taken_at"], unit="s", errors="coerce")
    df["hour"] = df["taken_at"].dt.hour
    df["weekday"] = df["taken_at"].dt.day_name()
    df["caption"] = df["caption"].fillna("")
    df["first_line_len"] = df["caption"].str.split("\n").str[0].str.len().fillna(0)
    df["hook_score"] = df["eng_score"] * (df["first_line_len"] / max(df["first_line_len"].max(), 1))

    # Ensure numeric columns exist for pages
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0).astype(int)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)

    # KPIs
    avg_eng = round(df["eng_score"].replace([np.inf, -np.inf], np.nan).dropna().mean() or 0, 4)
    total_followers = int(df_f["followers"].dropna().sum() or 0)

    # best_hour safe try
    try:
        best_hour = int(df.groupby("hour")["likes"].mean().idxmax())
    except Exception:
        best_hour = 0

    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="metric-card">⭐ Avg Engagement: {avg_eng}</div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card">👥 Total Followers: {total_followers:,}</div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card">⏰ Best Hour: {best_hour}:00</div>', unsafe_allow_html=True)

    # Competitor overlap
    overlap = 0.0
    if len(df_f) >= 2 and df_f["followers"].dropna().size >= 2:
        f_vals = df_f["followers"].dropna().astype(float).values
        if f_vals.max() > 0:
            overlap = float(np.min(f_vals) / np.max(f_vals) * 100)

    # Heatmap pivot
    pivot = df.pivot_table(values="eng_score", index="weekday", columns="hour", aggfunc="mean")

    # TABS
    tabs = st.tabs([
        "📊 Summary", "💥 Virality Predictor", "🌈 Heatmap", "🤝 Overlap", "🔥 Hook",
        "💬 Caption Analysis", "🏷️ Hashtag Insights", "⚔️ Brand Comparison", "🧾 Raw Data", "📈 Forecast"
    ])

    # ---------- SUMMARY TAB ----------
    with tabs[0]:
        st.subheader("Brand Comparison — Engagement Score Avg")
        avg_eng_df = df.groupby("username")["eng_score"].mean().reset_index()
        fig1 = px.bar(avg_eng_df, x="username", y="eng_score", text="eng_score",
                      color="eng_score", color_continuous_scale=px.colors.sequential.Plasma,
                      labels={"eng_score": "Engagement Score"},
                      title="🌟 Avg Engagement Score per Brand")
        fig1.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Followers per Brand")
        fig_followers = px.bar(df_f, x="username", y="followers", color="followers", text="followers",
                               color_continuous_scale=px.colors.sequential.Viridis,
                               title="👥 Followers per Brand")
        fig_followers.update_traces(texttemplate="%{text}", textposition="outside")
        st.plotly_chart(fig_followers, use_container_width=True)
        st.success(f"🔥 Best posting hour: {best_hour}:00")

    # ---------- VIRALITY TAB ----------
    with tabs[1]:
        tmp = df.dropna(subset=["likes", "views"])
        st.subheader("Reel Virality Predictor")
        if len(tmp) > 2 and tmp["views"].sum() > 0:
            X = tmp[["views"]].values
            y = tmp["likes"].values
            model = LinearRegression().fit(X, y)
            pred_views = st.number_input("Enter expected views for prediction", 1000, 10_000_000, 50000)
            pred_likes = int(model.predict(np.array([[pred_views]]))[0])
            st.write(f"💥 Predicted Likes for {pred_views:,} views: **{pred_likes:,}**")
        else:
            st.info("Not enough video/view data to build a virality model.")

    # ---------- HEATMAP TAB ----------
    with tabs[2]:
        st.subheader("Engagement Heatmap (Day x Hour)")
        if not pivot.empty:
            pivot_reset = pivot.reset_index().melt(id_vars="weekday", var_name="hour", value_name="eng_score")
            fig3 = px.density_heatmap(pivot_reset, x="hour", y="weekday", z="eng_score",
                                      color_continuous_scale='Inferno',
                                      labels={"eng_score": "Engagement Score"})
            fig3.update_layout(title="🌈 Engagement Heatmap",
                               yaxis={'categoryorder': 'array',
                                      'categoryarray': ['Monday', 'Tuesday', 'Wednesday',
                                                        'Thursday', 'Friday', 'Saturday', 'Sunday']})
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Not enough data to build a heatmap.")

    # ---------- OVERLAP TAB ----------
    with tabs[3]:
        st.subheader("Competitor Overlap %")
        st.write(f"🤝 Approx Overlap: **{overlap:0.1f}%**")

    # ---------- HOOK TAB ----------
    with tabs[4]:
        st.subheader("Hook Score — 1st Line Effect")
        hook_df = df.groupby("username")["hook_score"].mean().reset_index()
        fig2 = px.bar(hook_df, x="username", y="hook_score", text="hook_score",
                      color="hook_score", color_continuous_scale=px.colors.sequential.Viridis,
                      title="🔥 Hook Score by Brand")
        fig2.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------- CAPTION ANALYSIS TAB ----------
    with tabs[5]:
        st.subheader("💬 Caption Keyword Cloud")
        all_text = " ".join(df["caption"].dropna().astype(str))
        if all_text.strip():
            wc = WordCloud(width=900, height=500, background_color="white").generate(all_text)
            fig_wc, ax = plt.subplots(figsize=(12, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig_wc)
        else:
            st.info("No caption text available for word cloud.")

    # ---------- HASHTAG INSIGHTS TAB ----------
    with tabs[6]:
        st.subheader("🏷️ Hashtag Usage")
        hashtags_series = df["caption"].astype(str).str.findall(r"#\w+").explode().dropna().str.lower()
        if not hashtags_series.empty:
            top_hash = hashtags_series.value_counts().head(15)
            fig_hash = px.bar(x=top_hash.index, y=top_hash.values, title="Top 15 Hashtags",
                              labels={"x": "Hashtag", "y": "Count"}, color=top_hash.values,
                              color_continuous_scale="Bluered")
            st.plotly_chart(fig_hash, use_container_width=True)
            st.dataframe(top_hash.reset_index().rename(columns={"index": "hashtag", 0: "count"}).head(30))
        else:
            st.info("No hashtags detected in captions.")

    # ---------- BRAND COMPARISON TAB ----------
    with tabs[7]:
        st.subheader("⚔️ Brand Comparison — Engagement vs Followers")
        avg_eng_per_user = df.groupby("username")["eng_score"].mean().reset_index().rename(columns={"eng_score": "avg_eng_score"})
        dff_merge = df_f.merge(avg_eng_per_user, on="username", how="left")
        dff_merge["avg_eng_score"] = dff_merge["avg_eng_score"].fillna(0)
        fig_comp = px.scatter(dff_merge := dff_merge if False else dff_merge,
                              x="followers", y="avg_eng_score", color="username", size="followers",
                              title="Engagement vs Followers", labels={"avg_eng_score": "Avg Engagement Score"})
        st.plotly_chart(fig_comp, use_container_width=True)
        st.dataframe(dff_merge)

    # ---------- RAW DATA TAB ----------
    with tabs[8]:
        st.subheader("🧾 Raw Posts Data (first 50)")
        st.dataframe(df.head(50))

    # ---------- FORECAST TAB ----------
    with tabs[9]:
        st.info("Open the Forecast page from the sidebar (or use the Forecast tab to run quick forecasts).")
        st.write("For full forecast features open the dedicated Forecast page in the 'pages' folder.")

    # Save to session for pages
    st.session_state['df'] = df
    st.session_state['df_f'] = df_f

    # Export Excel
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="posts", index=False)
        df_f.to_excel(writer, sheet_name="followers", index=False)
    st.download_button("⬇ Export Excel", data=out.getvalue(), file_name="insta_results.xlsx")

    st.balloons()
