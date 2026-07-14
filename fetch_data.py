import os
import requests
from datetime import datetime

FIREBASE_URL = os.environ.get("FIREBASE_URL")

def update_all_data():
    api_url = "https://api.thaistock2d.com/history"
    
    try:
        response = requests.get(api_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            payload = {}
            
            for item in data:
                date_str = item.get("date")
                results = item.get("results", [])
                
                m_num = next((r.get("twod") for r in results if "12:" in r.get("open_time", "")), "--")
                e_num = next((r.get("twod") for r in results if "16:30" in r.get("open_time", "")), "--")
                
                payload[date_str] = {
                    "morning": m_num,
                    "evening": e_num
                }
            
            # Firebase ထဲကို အကုန်လုံး တစ်ခါတည်း ပို့လိုက်မယ် (Replace လုပ်လိုက်တာပါ)
            db_res = requests.put(f"{FIREBASE_URL}history.json", json=payload)
            
            if db_res.status_code == 200:
                print("အောင်မြင်သည်! ရက် ၁၀၀ စာနဲ့ ဒီနေ့ Data များ အကုန်ဝင်သွားပါပြီ။")
            else:
                print("Database Error:", db_res.text)
        else:
            print("API Error:", response.status_code)
    except Exception as e:
        print("System Error:", str(e))

if __name__ == "__main__":
    update_all_data()
