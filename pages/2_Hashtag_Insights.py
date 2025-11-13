import streamlit as st
import pandas as pd
import plotly.express as px
import re
 
st.set_page_config(page_title="Hashtag Insights", layout="wide")
st.title("🏷️ Hashtag & Keyword Insights")
st.write("Find which hashtags bring the most engagement.")
 
if 'df' not in st.session_state:
    st.error("No data found. Run Analyze on the main page first.")
    st.stop()
 
df = st.session_state['df'].copy()
if 'caption' not in df.columns:
    st.error("No 'caption' column found.")
    st.stop()
 
# Extract hashtags (lowercased)
df["hashtags"] = df["caption"].astype(str).apply(lambda x: re.findall(r"#(\w+)", x.lower()))
tags = df.explode("hashtags").dropna(subset=["hashtags"])
 
if tags.empty:
    st.info("No hashtags found.")
    st.stop()
 
tag_stats = tags.groupby("hashtags").agg(
    posts=("username", "count"),
    avg_likes=("likes", "mean"),
    avg_eng=("eng_score", "mean")
).reset_index().sort_values(by="avg_likes", ascending=False)
 
top_n = st.slider("Top N Hashtags", 5, 30, 10)
st.subheader("🔥 Top Hashtags by Avg Likes")
fig1 = px.bar(tag_stats.head(top_n), x="hashtags", y="avg_likes", color="avg_likes", text_auto=".0f")
st.plotly_chart(fig1, use_container_width=True)
 
st.subheader("📊 Hashtag Frequency")
freq = tags["hashtags"].value_counts().head(30).reset_index()
freq.columns = ["Hashtag", "Count"]
fig2 = px.treemap(freq, path=["Hashtag"], values="Count", title="Most Frequently Used Hashtags")
st.plotly_chart(fig2, use_container_width=True)
 
st.subheader("Top Hashtag Table")
st.dataframe(tag_stats.head(50))
 
