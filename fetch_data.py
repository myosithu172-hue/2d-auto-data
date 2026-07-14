import os
import requests

FIREBASE_URL = os.environ.get("FIREBASE_URL")

def update_all_data():
    api_url = "https://api.thaistock2d.com/live"
    # API ကို အယုံအကြည်ရှိအောင် Header ထည့်ပေးခြင်း
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # ဒေတာရမရ စစ်ဆေးခြင်း
            if "live" in data:
                print("Data ရရှိပါပြီ၊ Database သို့ ပို့နေပါသည်...")
                # ဒီနေရာမှာ Database ကို ပို့မယ့် logic ထည့်မယ်
                # Firebase URL ထဲကို ဒေတာတင်တဲ့အပိုင်း
                requests.put(f"{FIREBASE_URL}status.json", json={"last_update": "success"})
            else:
                print("API က ဒေတာမပေးပါ၊ ဖွဲ့စည်းပုံ ပြောင်းသွားပုံရသည်။")
        else:
            print(f"API Error: {response.status_code}")
            
    except Exception as e:
        print(f"System Error: {str(e)}")

if __name__ == "__main__":
    update_all_data()
