import streamlit as st
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
 
st.set_page_config(page_title="Sentiment & Caption Analysis", layout="wide")
st.title("🧠 Sentiment & Caption Analysis")
st.write("Analyze emotional tone and keyword patterns in your Instagram captions.")
 
if 'df' not in st.session_state:
    st.error("No data found. Run Analyze on the main page first.")
    st.stop()
 
df = st.session_state['df'].copy()
if df.empty:
    st.error("Loaded dataframe is empty.")
    st.stop()
 
if 'caption' not in df.columns:
    st.error("No 'caption' column found.")
    st.stop()
 
# Sentiment calculation
df["sentiment"] = df["caption"].astype(str).apply(lambda x: TextBlob(x).sentiment.polarity)
df["sentiment_label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.05 else ("Negative" if x < -0.05 else "Neutral"))
 
col1, col2 = st.columns([1.2, 1])
with col1:
    sentiment_counts = df["sentiment_label"].value_counts()
    fig1 = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="Overall Sentiment Distribution", color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig1, use_container_width=True)
 
with col2:
    avg_sentiment = df.groupby("sentiment_label")["likes"].mean().reset_index()
    fig2 = px.bar(avg_sentiment, x="sentiment_label", y="likes", title="Average Likes per Sentiment")
    st.plotly_chart(fig2, use_container_width=True)
 
# Wordcloud
st.subheader("💬 Common Words in Captions")
text = " ".join(df["caption"].dropna().astype(str))
if text.strip():
    wc = WordCloud(width=1000, height=500, background_color="white", colormap="coolwarm").generate(text)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
else:
    st.info("No caption text available for word cloud.")
