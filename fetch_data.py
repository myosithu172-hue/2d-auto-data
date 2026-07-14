import os
import requests
from datetime import datetime, timedelta

FIREBASE_URL = os.environ.get("FIREBASE_URL")

if not FIREBASE_URL:
    print("Error: FIREBASE_URL မရှိပါသဖြင့် ဆက်လက်လုပ်ဆောင်၍မရပါ။")
    exit(1)

if not FIREBASE_URL.endswith("/"):
    FIREBASE_URL += "/"

def get_accurate_2d(set_val, value_val):
    try:
        # ၁။ SET ရဲ့ နောက်ဆုံးဂဏန်းကို ယူပါမယ် (ဥပမာ - 1,621.11 -> 1)
        set_str = str(set_val).strip()
        digit_1 = set_str[-1] if set_str else "-"
        
        # ၂။ Value ရဲ့ ဒသမသမမတိုင်ခင် (အပြည့်ကိန်း) ရဲ့ နောက်ဆုံးဂဏန်းကို ယူပါမယ် (ဥပမာ - 43,537.24 -> 7)
        value_str = str(value_val).strip()
        if "." in value_str:
            value_integer = value_str.split(".")[0] # . ရဲ့ အရှေ့ပိုင်းကိုပဲ ဖြတ်ယူမယ်
        else:
            value_integer = value_str
        digit_2 = value_integer[-1] if value_integer else "-"
        
        if digit_1 != "-" and digit_2 != "-":
            return digit_1 + digit_2
        return "--"
    except:
        return "--"

def fetch_and_save():
    try:
        response = requests.get("https://api.thaistock2d.com/live", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            # API မှ SET နှင့် Value ကို တိုက်ရိုက်ရယူခြင်း
            set_val = str(result.get("live", {}).get("set", "")).strip()
            value_val = str(result.get("live", {}).get("value", "")).strip()
            
            # 2D တွက်ထုတ်မည့် ဖော်မြူလာအမှန်ဖြင့် တိတိကျကျ တွက်ချက်ခြင်း
            twod_number = get_accurate_2d(set_val, value_val)
            
            # မြန်မာစံတော်ချိန် တွက်ချက်ခြင်း
            now_utc = datetime.utcnow()
            mmt_time = now_utc + timedelta(hours=6, minutes=30)
            today_str = mmt_time.strftime("%Y-%m-%d")
            
            payload = {"updated_at": mmt_time.isoformat()}
            
            # နေ့လည် (၂) နာရီ မတိုင်ခင်ဆိုရင် morning၊ ကျော်ရင် evening
            if mmt_time.hour < 14:
                payload["morning"] = twod_number
                payload["morning_set"] = set_val
                payload["morning_value"] = value_val
            else:
                payload["evening"] = twod_number
                payload["evening_set"] = set_val
                payload["evening_value"] = value_val
            
            firebase_endpoint = f"{FIREBASE_URL}history/{today_str}.json"
            db_response = requests.patch(firebase_endpoint, json=payload)
            
            if db_response.status_code == 200:
                print(f"အောင်မြင်သည်! 2D: {twod_number} (SET: {set_val}, Value: {value_val})")
            else:
                print(f"Database Error: {db_response.text}")
                
        else:
            print(f"API Error - Code {response.status_code}")
            
    except Exception as e:
        print(f"System Error: {str(e)}")

if __name__ == "__main__":
    fetch_and_save()
