import os
import requests

FIREBASE_URL = os.environ.get("FIREBASE_URL")

def update_all_data():
    api_url = "https://api.thaistock2d.com/live"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # API မှလာသော result များကို ယူခြင်း
            results = data.get("result", [])
            payload = {}
            
            for item in results:
                date_str = item.get("date", "")
                if not date_str: continue
                
                # အကယ်၍ date အသစ်ဆိုရင် အကွက်အသစ်ဆောက်မယ်
                if date_str not in payload:
                    payload[date_str] = {"morning": "--", "evening": "--"}
                
                # မနက် (12:00) နှင့် ညနေ (16:30) ဂဏန်းများ ထည့်မယ်
                if "12:" in item.get("open_time", ""):
                    payload[date_str]["morning"] = item.get("twod", "--")
                elif "16:30" in item.get("open_time", ""):
                    payload[date_str]["evening"] = item.get("twod", "--")
            
            # အရေးကြီးဆုံး: ဒီနေရာမှာ history ထဲကို ပို့တာပါ
            if payload:
                db_res = requests.put(f"{FIREBASE_URL}history.json", json=payload)
                if db_res.status_code == 200:
                    print("အောင်မြင်သည်! Data များ history ထဲသို့ ရောက်ရှိသွားပါပြီ။")
                else:
                    print("Database Error:", db_res.text)
        else:
            print("API Error:", response.status_code)
    except Exception as e:
        print("System Error:", str(e))

if __name__ == "__main__":
    update_all_data()
