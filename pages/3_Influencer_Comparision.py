import streamlit as st
import pandas as pd
import plotly.express as px
 
st.set_page_config(page_title="Influencer Comparison", layout="wide")
st.title("🤝 Influencer / Brand Comparison")
st.write("Compare engagement, growth, and consistency across multiple accounts.")
 
if 'df' not in st.session_state or 'df_f' not in st.session_state:
    st.error("No data found. Run Analyze on the main page first.")
    st.stop()
 
df = st.session_state['df'].copy()
df_f = st.session_state['df_f'].copy()
 
# Build metrics per account from posts
metrics = df.groupby("username").agg(
    avg_likes=("likes", "mean"),
    avg_comments=("comments", "mean"),
    avg_eng_score=("eng_score", "mean"),
    posts=("username", "count")
).reset_index()
 
# Merge followers
metrics = metrics.merge(df_f, on="username", how="left")
metrics["followers"] = pd.to_numeric(metrics["followers"], errors="coerce").fillna(0).astype(int)
 
# Select accounts to compare
accounts = metrics["username"].tolist()
selected = st.multiselect("Select accounts to compare", accounts, default=accounts[:2] if len(accounts) >= 2 else accounts)
 
if not selected:
    st.warning("Select at least one account.")
    st.stop()
 
cmp = metrics[metrics["username"].isin(selected)]
 
# Radar chart (line_polar) requires melted long format
melted = cmp.melt(id_vars="username", value_vars=["avg_likes", "avg_comments", "avg_eng_score", "posts", "followers"],
                  var_name="metric", value_name="value")
fig_radar = px.line_polar(melted, r="value", theta="metric", color="username", line_close=True, markers=True,
                          title="Engagement Metrics Comparison (Radar)")
st.plotly_chart(fig_radar, use_container_width=True)
 
# Followers vs Engagement scatter
fig_scatter = px.scatter(cmp, x="followers", y="avg_eng_score", size="posts", color="username",
                         hover_data=["avg_likes", "avg_comments"], title="Followers vs Avg Engagement")
st.plotly_chart(fig_scatter, use_container_width=True)
 
st.subheader("Comparison Table")
st.dataframe(cmp.reset_index(drop=True))
 
