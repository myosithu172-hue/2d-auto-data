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
                if "12:" in time_str:  # ၁၂ နာရီပွဲ
                    morning_data = item
                elif "16:30" in time_str:  # ၄ နာရီခွဲပွဲ
                    evening_data = item
            
            # ၂။ တကယ်လို့ ပွဲမပြီးသေးလို့ Result မထွက်သေးရင် Live ကနေ တိတိကျကျ ယူမယ်
            live_set = str(data.get("live", {}).get("set", "")).replace(",", "").strip()
            live_value = str(data.get("live", {}).get("value", "")).replace(",", "").strip()
            
            live_twod = "--"
            try:
                if live_set and live_value:
                    val_int = live_value.split(".")[0]
                    live_twod = live_set[-1] + val_int[-1]
            except:
                pass
            
            # ၃။ မြန်မာစံတော်ချိန် တွက်ချက်ခြင်း
            now_utc = datetime.utcnow()
            mmt_time = now_utc + timedelta(hours=6, minutes=30)
            today_str = mmt_time.strftime("%Y-%m-%d")
            
            # အချိန်ကို သပ်ရပ်သော ပုံစံဖြင့်ပြောင်းခြင်း (ဥပမာ: 2026-07-14 12:01:00)
            formatted_time = mmt_time.strftime("%Y-%m-%d %H:%M:%S")
            
            payload = {}
            
            # နေ့လည် ၂ နာရီမတိုင်ခင်လား (သို့) ကျော်သွားပြီလား ခွဲခြားမယ်
            if mmt_time.hour < 14:
                # မနက်ပိုင်း Data စုစည်းမှု
                if morning_data:
                    twod = morning_data.get("twod", "")
                    set_val = morning_data.get("set", "")
                    value_val = morning_data.get("value", "")
                else:
                    twod = live_twod
                    set_val = live_set
                    value_val = live_value
                    
                payload["morning"] = {
                    "twod": twod,
                    "set": set_val,
                    "value": value_val,
                    "updated_at": formatted_time
                }
            else:
                # ညနေပိုင်း Data စုစည်းမှု
                if evening_data:
                    twod = evening_data.get("twod", "")
                    set_val = evening_data.get("set", "")
                    value_val = evening_data.get("value", "")
                else:
                    twod = live_twod
                    set_val = live_set
                    value_val = live_value
                    
                payload["evening"] = {
                    "twod": twod,
                    "set": set_val,
                    "value": value_val,
                    "updated_at": formatted_time
                }
                
            # ၄။ Firebase သို့ ပို့ခြင်း
            firebase_endpoint = f"{FIREBASE_URL}history/{today_str}.json"
            db_response = requests.patch(firebase_endpoint, json=payload)
            
            if db_response.status_code == 200:
                print(f"အောင်မြင်သည်! 2D ဒေတာများကို သပ်ရပ်သော Group ပုံစံဖြင့် သိမ်းဆည်းပြီးပါပြီ။")
            else:
                print(f"Database Error: {db_response.text}")
                
        else:
            print(f"API Error - Code {response.status_code}")
            
    except Exception as e:
        print(f"System Error: {str(e)}")

if __name__ == "__main__":
    fetch_and_save()
