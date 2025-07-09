from zlapi.models import Message
import requests
import random
import os
from config import *

des = {
    'version': "1.0.1",
    'credits': "LAMDev",
    'description': "Gửi ảnh gái"
}

# Loại bỏ kiểm tra quyền admin và nhóm, cho phép mọi người đều có thể sử dụng
def handle_anhgai_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        api_list = [
            "https://api-dowig.onrender.com/images/du",
            "https://api.sumiproject.net/images/du"
        ]
        
        def get_image_url():
            selected_api_url = random.choice(api_list)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            response = requests.get(selected_api_url, headers=headers)
            response.raise_for_status()
            json_data = response.json()
            if isinstance(json_data, dict) and 'url' in json_data:
                return json_data['url']
            elif isinstance(json_data, list) and len(json_data) > 0:
                return random.choice(json_data)
            else:
                raise ValueError("Dữ liệu trả về không hợp lệ hoặc không có trường 'url'")
        
        image_url = get_image_url()
        
        client.sendImage(
            image_url, 
            thread_id=thread_id,
            thread_type=thread_type,
            width=1200,
            height=1600,
            message=Message(text="🖼️ Ảnh du cho bạn nè! 💖"),
            ttl=100000  # Thêm TTL
        )
    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=300000)
    except ValueError as e:
        error_message = Message(text=f"Lỗi dữ liệu: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=300000)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=300000)

def get_tmii():
    return {
        'anhdu': handle_anhgai_command
    }
