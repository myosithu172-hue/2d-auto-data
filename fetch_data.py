import os
import requests
from datetime import datetime, timedelta

FIREBASE_URL = os.environ.get("FIREBASE_URL")

if not FIREBASE_URL:
    print("Error: FIREBASE_URL မရှိပါသဖြင့် ဆက်လက်လုပ်ဆောင်၍မရပါ။")
    exit(1)

if not FIREBASE_URL.endswith("/"):
    FIREBASE_URL += "/"

def get_2d_number(result):
    # API က 2D ဂဏန်းတိုက်ရိုက်ပေးရင် ယူမယ်
    twod = str(result.get("live", {}).get("twod", "")).strip()
    if twod and twod != "None" and len(twod) == 2:
        return twod
        
    # တိုက်ရိုက်မပေးရင် SET နဲ့ Value ထဲက နောက်ဆုံးဂဏန်းတွေကို ယူပေါင်းမယ်
    set_val = str(result.get("live", {}).get("set", "")).strip()
    value_val = str(result.get("live", {}).get("value", "")).strip()
    
    def extract_last_digit(s):
        s = s.replace(",", "").replace(".", "").strip()
        return s[-1] if s else "-"
        
    try:
        return extract_last_digit(set_val) + extract_last_digit(value_val)
    except:
        return "--"

def fetch_and_save():
    try:
        response = requests.get("https://api.thaistock2d.com/live", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            twod_number = get_2d_number(result)
            
            # မြန်မာစံတော်ချိန် (UTC +6:30) သို့ ပြောင်းခြင်း
            now_utc = datetime.utcnow()
            mmt_time = now_utc + timedelta(hours=6, minutes=30)
            today_str = mmt_time.strftime("%Y-%m-%d")
            
            # နေ့လည် ၁၄:၀၀ (၂ နာရီ) မတိုင်ခင်ဆိုရင် morning၊ ကျော်သွားရင် evening လို့ သတ်မှတ်မယ်
            payload = {"updated_at": mmt_time.isoformat()}
            if mmt_time.hour < 14:
                payload["morning"] = twod_number
            else:
                payload["evening"] = twod_number
            
            firebase_endpoint = f"{FIREBASE_URL}history/{today_str}.json"
            
            # PATCH ကိုသုံးတာဖြစ်လို့ ရှိပြီးသားဒေတာ (ဥပမာ မနက်ပိုင်း) ကို မဖျက်ဘဲ အသစ် (ညနေပိုင်း) ကိုပဲ ထပ်ထည့်ပေးပါမည်
            db_response = requests.patch(firebase_endpoint, json=payload)
            
            if db_response.status_code == 200:
                print(f"အောင်မြင်သည်! {today_str} အတွက် ({twod_number}) ကို သိမ်းဆည်းပြီးပါပြီ။")
            else:
                print(f"Database သို့ ပို့ရန် အဆင်မပြေပါ- {db_response.text}")
                
        else:
            print(f"API ထံမှ ဒေတာမရရှိပါ- Status Code {response.status_code}")
            
    except Exception as e:
        print(f"အမှားအယွင်း ဖြစ်ပွားခဲ့သည်- {str(e)}")

if __name__ == "__main__":
    fetch_and_save()
