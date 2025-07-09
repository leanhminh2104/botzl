import time
import random
import requests
from zlapi.models import Message, ThreadType
from datetime import datetime
import pytz
import json
import os

time_messages = {
    "01:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "01:15": "..rs",
    "02:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "02:15": "..rs",
    "03:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "03:15": "..rs",
    "04:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "04:15": "..rs",
    "05:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "05:15": "..rs",
    "06:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "06:15": "..rs",
    "07:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "07:15": "..rs",
    "08:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "08:15": "..rs",
    "09:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "09:15": "..rs",
    "10:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "10:15": "..rs",
    "11:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "11:15": "..rs",
    "12:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "12:15": "..rs",
    "13:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "13:15": "..rs",
    "14:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "14:15": "..rs",
    "15:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "15:15": "..rs",
    "16:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "16:15": "..rs",
    "17:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "17:15": "..rs",
    "18:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "18:15": "..rs",
    "19:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "19:15": "..rs",
    "20:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "20:15": "..rs",
    "21:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "21:15": "..rs",
    "22:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "22:15": "..rs",
    "23:14": "Bot Sẽ Reset Sau Một Phút Nữa", 
    "23:15": "..rs"
}


vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

def load_duyetbox_data():
    file_path = 'modules/cache/quanly.json'
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

# ✅ Hàm chính
def start_auto(client):
    approved_group_ids = load_duyetbox_data()
    last_sent_key = None

    while True:
        now = datetime.now(vn_tz)
        current_time_key = now.strftime("%H:%M")  # vd: "03:14"
        current_second = now.second

        if current_time_key in time_messages and current_second == 0:
            if current_time_key != last_sent_key:
                message = time_messages[current_time_key]
                for thread_id in approved_group_ids:
                    gui = Message(text=f"{message}")
                    try:
                        client.sendMessage(
                            message=gui,
                            thread_id=thread_id,
                            thread_type=ThreadType.GROUP,
                            ttl=5000  # nếu API hỗ trợ
                        )
                        print(f"[{now.strftime('%H:%M:%S')}] ✅ Gửi tới {thread_id}: {message}")
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"❌ Lỗi gửi tới {thread_id}: {e}")
                last_sent_key = current_time_key

        time.sleep(1)
