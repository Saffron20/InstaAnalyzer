import os
import time
import requests
import pandas as pd

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN env variable not found. Set it first.")

ACTOR_ID = "apify~instagram-scraper"


def scrape_instagram(url):
    start_res = requests.post(
        f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}",
        json={
            "directUrls": [url],     # <--- FIXED
            "resultsType": "posts",
            "resultsLimit": 50
        }
    ).json()

    print("START RESPONSE:", start_res)

    run_id = start_res["data"]["id"]
    print("Run started:", run_id)

    while True:
        status_res = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
        ).json()
        status = status_res["data"]["status"]
        print("Status:", status)

        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

        time.sleep(2)

    if status != "SUCCEEDED":
        print("Run did not succeed:", status)
        return

    dataset_id = status_res["data"]["defaultDatasetId"]
    print("Dataset:", dataset_id)

    items = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
    ).json()

    df = pd.DataFrame(items)
    df.to_csv("result.csv", index=False)
    print("Saved result.csv")


scrape_instagram("https://www.instagram.com/humansofny/")
