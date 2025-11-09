import pandas as pd
import re

df = pd.read_csv("result.csv")

# keep only needed columns IF present
keep_cols = [
    "ownerUsername",
    "likesCount",
    "commentsCount",
    "caption",
    "hashtags",
    "url",
    "firstComment",
    "alt",
    "timestamp"
]

df = df[[c for c in keep_cols if c in df.columns]]

# normalize
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# engagement rate (%)
df["engagement_rate"] = (
    (df["likesCount"].fillna(0) + df["commentsCount"].fillna(0))
    / 100000.0
) * 100

# extract caption length
df["caption_len"] = df["caption"].fillna("").apply(len)

# extract hashtags properly
def extract_hashtags(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        return re.findall(r"#\w+", x)
    return []

df["hashtags_list"] = df["caption"].apply(extract_hashtags)

df.to_csv("clean.csv", index=False, encoding="utf-8-sig")

print("clean.csv saved ")
