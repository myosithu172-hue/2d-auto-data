import os
import requests

FIREBASE_URL = os.environ.get("FIREBASE_URL")

def fetch_and_save_history():
    # မိတ်ဆွေပြောတဲ့ History API လင့်ခ်
    api_url = "https://api.thaistock2d.com/history"
    
    try:
        response = requests.get(api_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            payload = {}
            
            for item in data:
                date_str = item.get("date")
                results = item.get("results", [])
                
                # တစ်နေ့တာအတွက် ဂဏန်းနှစ်ခုကိုပဲ ရှာမယ်
                m_num = next((r.get("twod") for r in results if "12:" in r.get("open_time", "")), None)
                e_num = next((r.get("twod") for r in results if "16:30" in r.get("open_time", "")), None)
                
                # Database ထဲမှာ ရှင်းရှင်းလင်းလင်းဖြစ်အောင် morning/evening နဲ့ပဲ သိမ်းမယ်
                if m_num or e_num:
                    payload[date_str] = {}
                    if m_num: payload[date_str]["morning"] = m_num
                    if e_num: payload[date_str]["evening"] = e_num
            
            # Firebase သို့ ပို့ခြင်း (History တစ်ခုလုံးကို အသစ်ပြန်တင်သလိုဖြစ်မယ်)
            db_res = requests.patch(f"{FIREBASE_URL}history.json", json=payload)
            
            if db_res.status_code == 200:
                print("အောင်မြင်သည်! ရက် ၁၀၀ စာ Data များ အော်တိုဝင်သွားပါပြီ။")
            else:
                print("Database Error:", db_res.text)
        else:
            print("API Error:", response.status_code)
    except Exception as e:
        print("System Error:", str(e))

if __name__ == "__main__":
    fetch_and_save_history()
