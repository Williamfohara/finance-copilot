import os

import requests
from dotenv import load_dotenv

load_dotenv()


def refresh_qbo_token():
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    auth = (os.getenv("QUICKBOOKS_CLIENT_ID"), os.getenv("QUICKBOOKS_CLIENT_SECRET"))
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("QB_REFRESH_TOKEN"),
    }

    response = requests.post(url, headers=headers, data=data, auth=auth)
    if response.status_code == 200:
        tokens = response.json()
        print("✅ Refreshed access token.")
        return tokens
    else:
        print("❌ Failed to refresh token:", response.json())
        return None
