import os
import requests

FIREBASE_URL = os.environ.get("FIREBASE_URL")

def update_all_data():
    # အလုပ်လုပ်ဖို့ ပိုသေချာတဲ့ API လင့်ခ်အသစ်
    api_url = "https://api.thaistock2d.com/live" 
    
    try:
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # API ဖွဲ့စည်းပုံအသစ်အရ ဒေတာကို ပြန်ခွဲထုတ်ခြင်း
            results = data.get("result", [])
            payload = {}
            
            for item in results:
                date_str = item.get("date", "")
                twod = item.get("twod", "--")
                
                if date_str:
                    if date_str not in payload:
                        payload[date_str] = {"morning": "--", "evening": "--"}
                    
                    if "12:" in item.get("open_time", ""):
                        payload[date_str]["morning"] = twod
                    elif "16:30" in item.get("open_time", ""):
                        payload[date_str]["evening"] = twod
            
            # Firebase ထဲသို့ ပို့ခြင်း
            if payload:
                db_res = requests.put(f"{FIREBASE_URL}history.json", json=payload)
                if db_res.status_code == 200:
                    print("အောင်မြင်သည်! ဒေတာများ သိမ်းဆည်းပြီးပါပြီ။")
                else:
                    print("Database Error:", db_res.text)
            else:
                print("Data မရှိပါ။")
        else:
            print("API Error Code:", response.status_code)
            
    except Exception as e:
        print("System Error:", str(e))

if __name__ == "__main__":
    update_all_data()
