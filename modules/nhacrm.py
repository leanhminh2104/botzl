from zlapi.models import Message
import requests
import random
from config import *

des = {
    'version': "1.0.2",
    'credits': "DuongNgoc",
    'description': "Gửi video nhac remix"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_nhacremix_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    uptime_message = "Musi. Remix Random For You\n[ Dương Ngọc Yêu Quỳnh Anh ]"
    message_to_send = Message(text=uptime_message)
    
    url = 'https://raw.githubusercontent.com/trannguyen-shiniuem/trannguyen-shiniuem/refs/heads/main/nhacremix.json'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Nếu API trả về list, chọn một URL ngẫu nhiên
        if isinstance(data, list) and len(data) > 0:
            video_url = random.choice(data)  # Chọn ngẫu nhiên một video từ danh sách
        else:
            raise ValueError("API trả về dữ liệu không đúng định dạng!")

        # Kiểm tra nếu không có video_url thì báo lỗi
        if not video_url.startswith("http"):
            error_message = Message(text="❌ Không tìm thấy video nào hợp lệ!")
            client.sendMessage(error_message, thread_id=thread_id, thread_type=thread_type)
            return

        thumbnail_url = 'https://files.catbox.moe/jbo6uy.jpg'
        duration = '100'

        client.sendRemoteVideo(
            video_url, 
            thumbnail_url,
            duration=duration,
            message=message_to_send,
            thread_id=thread_id,
            thread_type=thread_type,
            width=1080,
            height=1920
        )
        
    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"❌ Lỗi khi lấy API: {str(e)}")
        client.sendMessage(error_message, thread_id=thread_id, thread_type=thread_type)
    except Exception as e:
        error_message = Message(text=f"❌ Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id=thread_id, thread_type=thread_type)

def get_tmii():
    return {
        'nhacrm': handle_nhacremix_command
    }
    