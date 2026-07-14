import os
import requests
from datetime import datetime

# Firebase URL ကို Environment Variable ကနေ လှမ်းယူမယ်
FIREBASE_URL = os.environ.get("FIREBASE_URL")

if not FIREBASE_URL:
    print("Error: FIREBASE_URL မရှိပါသဖြင့် ဆက်လက်လုပ်ဆောင်၍မရပါ။")
    exit(1)

# Firebase URL အဆုံးမှာ / ပါမပါ စစ်ဆေးပြင်ဆင်ခြင်း
if not FIREBASE_URL.endswith("/"):
    FIREBASE_URL += "/"

def fetch_and_save():
    try:
        # ဒီနေရာမှာ Live 2D Result ပြပေးတဲ့ ယုံကြည်စိတ်ချရတဲ့ Public API ကနေ Data လှမ်းယူပါတယ်
        # (ဥပမာအနေနဲ့ ပုံသေနမူနာ သုံးထားပါတယ်၊ မိမိသုံးချင်တဲ့ API Endpoint သို့ ပြောင်းလဲနိုင်သည်)
        response = requests.get("https://api.thaistock2d.com/live", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            # လက်ရှိရက်စွဲကို ရယူခြင်း (Format: YYYY-MM-DD)
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            # API မှရလာသော မနက်ခင်းနှင့် ညနေခင်း ဂဏန်းများကို ထုတ်ယူခြင်း
            # (မှတ်ချက် - မိမိသုံးမည့် API ရဲ့ JSON Key အမည်များအပေါ် မူတည်ပြီး ပြင်ဆင်နိုင်သည်)
            morning_num = result.get("live", {}).get("set", "-")  # နမူနာဂဏန်း
            evening_num = result.get("live", {}).get("value", "-") # နမူနာဂဏန်း
            
            payload = {
                "morning": morning_num,
                "evening": evening_num,
                "updated_at": datetime.now().isoformat()
            }
            
            # Firebase Realtime Database ရဲ့ REST API သို့ PATCH Request ဖြင့် လှမ်းပို့ခြင်း
            # ဒေတာများကို နေ့ရက်အလိုက် စနစ်တကျ သိမ်းဆည်းပေးမည်ဖြစ်သည်
            firebase_endpoint = f"{FIREBASE_URL}history/{today_str}.json"
            db_response = requests.patch(firebase_endpoint, json=payload)
            
            if db_response.status_code == 200:
                print(f"အောင်မြင်သည်! {today_str} အတွက် ဂဏန်းဒေတာများကို သိမ်းဆည်းပြီးပါပြီ။")
            else:
                print(f"Database သို့ ပို့ရန် အဆင်မပြေပါ- {db_response.text}")
                
        else:
            print(f"API ထံမှ ဒေတာမရရှိပါ- Status Code {response.status_code}")
            
    except Exception as e:
        print(f"အမှားအယွင်း ဖြစ်ပွားခဲ့သည်- {str(e)}")

if __name__ == "__main__":
    fetch_and_save()
