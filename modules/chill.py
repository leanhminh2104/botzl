from zlapi import ZaloAPI
from zlapi.models import *
import os
import random
import json
import requests
from config import *

des = {
    'version': "1.0.0",
    'credits': "LAMDev",
    'description': "Gửi video ngẫu nhiên từ danh sách JSON"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_chill_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    try:
        # Đọc dữ liệu từ file JSON chứa danh sách video
        with open('Api/chill.json', 'r', encoding='utf-8') as json_file:
            video_data = json.load(json_file)

        if video_data and isinstance(video_data, list):
            # Lấy video URL ngẫu nhiên từ danh sách
            video_url = random.choice(video_data)
            thumbnail_url = "https://sv1.anhsieuviet.com/2025/04/16/profile-facebook.png"  # URL ảnh thu nhỏ mặc định
            duration = 15000  # Độ dài video (ms)
            width = 1080
            height = 1920

            # Lấy nội dung tin nhắn từ API
            text_response = requests.get("https://api.sumiproject.net/text/thinh")
            if text_response.status_code == 200:
                text_data = text_response.json()
                content = text_data.get("data", "Nội dung không có sẵn")
            else:
                content = "Nội dung không thể tải được."

            # Gửi video qua API
            client.sendRemoteVideo(
                videoUrl=video_url,
                thumbnailUrl=thumbnail_url,
                duration=duration,
                thread_id=thread_id,
                thread_type=thread_type,
                message=Message(text=content),
                width=1920,  # Kích thước chiều rộng của video
                height=980,  # Kích thước chiều cao của video
                ttl=600000
            )
        else:
            client.send(
                Message(text="Danh sách video rỗng hoặc không hợp lệ."),
                thread_id=thread_id,
                thread_type=thread_type,
                ttl=30000
            )
    except Exception as e:
        # Xử lý lỗi và gửi thông báo
        error_text = f"Lỗi xảy ra: {str(e)}"
        client.send(
            Message(text=error_text),
            thread_id=thread_id,
            thread_type=thread_type,
            ttl=30000
        )

def get_tmii():
    return {
        'chill': handle_chill_command
    }
