import os
import requests
import json

FIREBASE_URL = os.environ.get("FIREBASE_URL")

def update_all_data():
    api_url = "https://api.thaistock2d.com/history"
    
    try:
        # API ကို ခေါ်ယူခြင်း
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            payload = {}
            
            # API ကပေးတဲ့ List ထဲက Data တွေကို စနစ်တကျ ပြန်စီမယ်
            for item in data:
                date_str = item.get("date")
                results = item.get("results", [])
                
                # မနက် (12:00) နှင့် ညနေ (16:30) ပွဲများကို ခွဲထုတ်ခြင်း
                morning = next((r.get("twod") for r in results if "12:" in r.get("open_time", "")), None)
                evening = next((r.get("twod") for r in results if "16:30" in r.get("open_time", "")), None)
                
                # Data တစ်ခုခုရှိမှသာ သိမ်းဆည်းမည်
                if morning or evening:
                    payload[date_str] = {
                        "morning": morning if morning else "--",
                        "evening": evening if evening else "--"
                    }
            
            # Firebase သို့ ပို့ခြင်း (အဟောင်းဖျက် အသစ်တင်)
            if payload:
                db_res = requests.put(f"{FIREBASE_URL}history.json", json=payload)
                if db_res.status_code == 200:
                    print("အောင်မြင်သည်! ရက် ၁၀၀ စာ Data အကုန်လုံး အပ်ဒိတ်လုပ်ပြီးပါပြီ။")
                else:
                    print("Database Error:", db_res.text)
            else:
                print("API ထံမှ Data မရရှိပါ။")
        else:
            print("API Error Code:", response.status_code)
            
    except Exception as e:
        print("System Error:", str(e))

if __name__ == "__main__":
    update_all_data()
