import os
import requests

FIREBASE_URL = os.environ.get("FIREBASE_URL")

def update_all_data():
    api_url = "https://api.thaistock2d.com/live"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("result", [])
            
            payload = {}
            # API မှ ရရှိသော ရက်စွဲအလိုက် ဒေတာများကို စုစည်းခြင်း
            for item in results:
                date_str = item.get("date", "")
                if not date_str: continue
                
                if date_str not in payload:
                    payload[date_str] = {"morning": "--", "evening": "--"}
                
                # အချိန်အလိုက် ဂဏန်းခွဲခြင်း
                if "12:" in item.get("open_time", ""):
                    payload[date_str]["morning"] = item.get("twod", "--")
                elif "16:30" in item.get("open_time", ""):
                    payload[date_str]["evening"] = item.get("twod", "--")
            
            # Firebase သို့ ပို့ခြင်း
            if payload:
                db_res = requests.put(f"{FIREBASE_URL}history.json", json=payload)
                if db_res.status_code == 200:
                    print("အောင်မြင်သည်! ဒေတာများ Database ထဲသို့ ရောက်ရှိသွားပါပြီ။")
                else:
                    print(f"Database Error: {db_res.text}")
        else:
            print(f"API Error: {response.status_code}")
            
    except Exception as e:
        print(f"System Error: {str(e)}")

if __name__ == "__main__":
    update_all_data()
