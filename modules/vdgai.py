from zlapi import ZaloAPI
from zlapi.models import *
import os
import random
import json
import requests
from config import *

des = {
    'version': "1.0.3",
    'credits': "LAMDev",
    'description': "Gửi video gái ngẫu nhiên từ nhiều API"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  

# Danh sách nhiều API
VIDEO_API_LIST = [
    "https://api.sumiproject.net/video/videogai",
    "https://api-dowig.onrender.com/images/videogaixinh",
    "https://api-dowig.onrender.com/images/autosend"
]

def get_video_url():
    retries = 3

    for api_url in VIDEO_API_LIST:
        for attempt in range(retries):
            try:
                response = requests.get(api_url, timeout=5)
                response.raise_for_status()
                data = response.json()
                video_url = data.get('url')
                if video_url:
                    return video_url
            except Exception as e:
                if attempt == retries - 1:
                    continue  # Thử API tiếp theo nếu hết lượt
                else:
                    continue

    raise Exception("❌ Không thể lấy video từ bất kỳ API nào.")

def get_file_size(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        size_bytes = int(response.headers.get('content-length', 0))
        return size_bytes
    except:
        return 0

def handle_chill_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return

    try:
        video_url = get_video_url()

        file_size = get_file_size(video_url)
        max_size = 100 * 1024 * 1024  # 100MB

        if file_size > max_size:
            client.send(
                Message(text="❌ Video quá nặng (>100MB), không thể gửi!"),
                thread_id=thread_id,
                thread_type=thread_type,
                ttl=30000
            )
            return

        thumbnail_url = "https://files.catbox.moe/jbo6uy.jpg"
        duration = 15000
        width = 720
        height = 1280

        # Gửi video
        client.sendRemoteVideo(
            thread_id=thread_id,
            thread_type=thread_type,
            videoUrl=video_url,
            thumbnailUrl=thumbnail_url,
            duration=duration,
            width=width,
            height=height,
            message=Message(text="🎬 Video gái cho bạn nè! 💖"),
            ttl=60000
        )

    except Exception as e:
        error_text = f"❌ Lỗi xảy ra: {str(e)}"
        client.send(
            Message(text=error_text),
            thread_id=thread_id,
            thread_type=thread_type,
            ttl=30000
        )

def get_tmii():
    return {
        'vdgai': handle_chill_command
    }
