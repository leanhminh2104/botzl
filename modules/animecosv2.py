from zlapi.models import Message
import requests
from config import *

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "Gửi video anime chill"
}

# Kiểm tra quyền truy cập của nhóm
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  

# Xử lý lệnh gửi video anime chill
def handle_vdgai_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    
    uptime_message = "Video Cosplay For You\n[ LAMDev - SIEUTHIMMO ]"
    message_to_send = Message(text=uptime_message)
    
    url = 'https://api-dowig.onrender.com/images/videochill'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        # Gửi yêu cầu API và nhận dữ liệu
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Kiểm tra nếu có lỗi từ API

        data = response.json()

        # Lấy URL video từ dữ liệu trả về
        video_url = data.get('url', None)

        # Kiểm tra nếu không có video URL hợp lệ
        if not video_url or not video_url.startswith("http"):
            error_message = Message(text="❌ Không tìm thấy video nào hợp lệ!")
            client.sendMessage(error_message, thread_id=thread_id, thread_type=thread_type, ttl = 10000)
            return

        # Gửi video nếu URL hợp lệ
        thumbnail_url = 'https://sv1.anhsieuviet.com/2025/04/16/profile-facebook.png'
        duration = '100'

        client.sendRemoteVideo(
            video_url, 
            thumbnail_url,
            duration=duration,
            message=message_to_send,
            thread_id=thread_id,
            thread_type=thread_type,
            width=1920,  # Kích thước chiều rộng của video
            height=980,  # Kích thước chiều cao của video
            ttl=300000
        )
        
    except requests.exceptions.RequestException as e:
        # Lỗi khi gọi API
        error_message = Message(text=f"❌ Lỗi khi lấy API: {str(e)}")
        client.sendMessage(error_message, thread_id=thread_id, thread_type=thread_type, ttl = 10000)
        
    except Exception as e:
        # Lỗi chung nếu có vấn đề khác
        error_message = Message(text=f"❌ Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id=thread_id, thread_type=thread_type, ttl = 10000)

# Hàm lấy thông tin lệnh
def get_tmii():
    return {
        'vdcosv2': handle_vdgai_command
    }
