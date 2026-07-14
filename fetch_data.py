import os
import requests
from datetime import datetime, timedelta

FIREBASE_URL = os.environ.get("FIREBASE_URL")

if not FIREBASE_URL:
    print("Error: FIREBASE_URL မရှိပါ။")
    exit(1)

if not FIREBASE_URL.endswith("/"):
    FIREBASE_URL += "/"

def fetch_and_save():
    try:
        response = requests.get("https://api.thaistock2d.com/live", timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data.get("result", [])
            
            # မနက် (12:01) နှင့် ညနေ (16:30) ပွဲများရှာခြင်း
            m_num = next((item.get("twod") for item in results if "12:" in item.get("open_time", "")), None)
            e_num = next((item.get("twod") for item in results if "16:30" in item.get("open_time", "")), None)
            
            # အချိန်နှင့် ရက်စွဲ
            now_mmt = datetime.utcnow() + timedelta(hours=6, minutes=30)
            today = now_mmt.strftime("%Y-%m-%d")
            
            payload = {}
            if m_num: payload["morning"] = m_num
            if e_num: payload["evening"] = e_num
            
            if payload:
                # ဒေတာတင်ခြင်း
                db_res = requests.patch(f"{FIREBASE_URL}history/{today}.json", json=payload)
                if db_res.status_code == 200:
                    print(f"အောင်မြင်သည်: {payload}")
                else:
                    print("Database Error:", db_res.text)
        else:
            print("API Error")
    except Exception as e:
        print("System Error:", str(e))

if __name__ == "__main__":
    fetch_and_save()
