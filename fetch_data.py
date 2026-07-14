import os
import requests
from datetime import datetime, timedelta

FIREBASE_URL = os.environ.get("FIREBASE_URL")

if not FIREBASE_URL:
    print("Error: FIREBASE_URL မရှိပါသဖြင့် ဆက်လက်လုပ်ဆောင်၍မရပါ။")
    exit(1)

if not FIREBASE_URL.endswith("/"):
    FIREBASE_URL += "/"

def fetch_and_save():
    try:
        response = requests.get("https://api.thaistock2d.com/live", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # ၁။ App တွေလိုမျိုး ပြီးသွားတဲ့ ဂဏန်းအသေ (Result) တွေကို အရင်ရှာမယ်
            results_list = data.get("result", [])
            morning_data = None
            evening_data = None
            
            for item in results_list:
                time_str = item.get("open_time", "")
                if "12:" in time_str:  # ၁၂ နာရီပွဲ (မနက်ပိုင်း)
                    morning_data = item.get("twod")
                elif "16:30" in time_str:  # ၄ နာရီခွဲပွဲ (ညနေပိုင်း)
                    evening_data = item.get("twod")
            
            # ၂။ တကယ်လို့ ပွဲမပြီးသေးလို့ Result မထွက်သေးရင် Live ကနေ တိတိကျကျ အရန်တွက်မယ်
            live_set = str(data.get("live", {}).get("set", "")).replace(",", "").strip()
            live_value = str(data.get("live", {}).get("value", "")).replace(",", "").strip()
            
            live_twod = "--"
            try:
                if live_set and live_value:
                    val_int = live_value.split(".")[0]  # ဒသမနောက်က ဂဏန်းများကို ဖြတ်ထုတ်ခြင်း
                    live_twod = live_set[-1] + val_int[-1]
            except:
                pass
            
            # ၃။ မြန်မာစံတော်ချိန် တွက်ချက်ခြင်း
            now_utc = datetime.utcnow()
            mmt_time = now_utc + timedelta(hours=6, minutes=30)
            today_str = mmt_time.strftime("%Y-%m-%d")
            
            payload = {"updated_at": mmt_time.isoformat()}
            final_number = "--"
            
            # နေ့လည် ၂ နာရီမတိုင်ခင်လား (သို့) ကျော်သွားပြီလား ခွဲခြားမယ်
            if mmt_time.hour < 14:
                # မနက်ပိုင်းအတွက် (Result ရှိရင် ယူမယ်၊ မရှိရင် Live ကိုယူမယ်)
                final_number = morning_data if morning_data else live_twod
                payload["morning"] = final_number
            else:
                # ညနေပိုင်းအတွက် (Result ရှိရင် ယူမယ်၊ မရှိရင် Live ကိုယူမယ်)
                final_number = evening_data if evening_data else live_twod
                payload["evening"] = final_number
                
            # ၄။ Firebase သို့ ပို့ခြင်း
            firebase_endpoint = f"{FIREBASE_URL}history/{today_str}.json"
            db_response = requests.patch(firebase_endpoint, json=payload)
            
            if db_response.status_code == 200:
                print(f"အောင်မြင်သည်! 2D: {final_number} ကို App အတိုင်း တိုက်ရိုက် သိမ်းဆည်းပြီးပါပြီ။")
            else:
                print(f"Database Error: {db_response.text}")
                
        else:
            print(f"API Error - Code {response.status_code}")
            
    except Exception as e:
        print(f"System Error: {str(e)}")

if __name__ == "__main__":
    fetch_and_save()
