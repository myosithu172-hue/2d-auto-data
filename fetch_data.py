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
            
            # App တွေလိုမျိုး ပြီးသွားတဲ့ ဂဏန်းအသေ (Result) တွေကို အရင်ရှာမယ်
            results_list = data.get("result", [])
            morning_data = None
            evening_data = None
            
            for item in results_list:
                time_str = item.get("open_time", "")
                if "12:" in time_str:
                    morning_data = item
                elif "16:30" in time_str:
                    evening_data = item
            
            # Live ဒေတာ ယူခြင်း (Result မထွက်သေးချိန်အတွက်)
            live_set = str(data.get("live", {}).get("set", "")).strip()
            live_value = str(data.get("live", {}).get("value", "")).strip()
            
            live_twod = "--"
            try:
                if live_set and live_value:
                    val_int = live_value.replace(",", "").split(".")[0]
                    live_twod = live_set.replace(",", "")[-1] + val_int[-1]
            except:
                pass
            
            # အချိန် တွက်ချက်ခြင်း
            now_utc = datetime.utcnow()
            mmt_time = now_utc + timedelta(hours=6, minutes=30)
            today_str = mmt_time.strftime("%Y-%m-%d")
            
            # သပ်ရပ်သော အချိန် Format (ဥပမာ: 2026-07-14 12:01:00)
            formatted_time = mmt_time.strftime("%Y-%m-%d %H:%M:%S")
            
            payload = {"updated_at": formatted_time}
            
            # နေ့လည် ၂ နာရီမတိုင်ခင် (မနက်ပိုင်း) နှင့် ကျော်လွန်ချိန် (ညနေပိုင်း) ခွဲခြားခြင်း
            if mmt_time.hour < 14:
                payload["morning"] = morning_data.get("twod", "") if morning_data else live_twod
                payload["morning_set"] = morning_data.get("set", "") if morning_data else live_set
                payload["morning_value"] = morning_data.get("value", "") if morning_data else live_value
            else:
                payload["evening"] = evening_data.get("twod", "") if evening_data else live_twod
                payload["evening_set"] = evening_data.get("set", "") if evening_data else live_set
                payload["evening_value"] = evening_data.get("value", "") if evening_data else live_value
                
            firebase_endpoint = f"{FIREBASE_URL}history/{today_str}.json"
            db_response = requests.patch(firebase_endpoint, json=payload)
            
            if db_response.status_code == 200:
                print("အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
            else:
                print("Error:", db_response.text)
                
        else:
            print("API Error - Code", response.status_code)
            
    except Exception as e:
        print("System Error:", str(e))

if __name__ == "__main__":
    fetch_and_save()
