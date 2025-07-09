from zlapi.models import Message
import time
import os
import requests
import random
from config import *

des = {
    'version': "1.0.1",
    'credits': "LAMDev",
    'description': "Xem thời gian bot hoạt động"
}

start_time = time.time()
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_uptime_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    if author_id not in ADMIN:
        client.replyMessage(
            Message(text="🚫 Bạn không có quyền sử dụng lệnh này!"), 
            message_object, thread_id, thread_type,
            ttl=30000
        )
        return
    try:
        # Tính thời gian bot hoạt động
        current_time = time.time()
        uptime_seconds = int(current_time - start_time)

        days = uptime_seconds // (24 * 3600)
        uptime_seconds %= (24 * 3600)
        hours = uptime_seconds // 3600
        uptime_seconds %= 3600
        minutes = uptime_seconds // 60
        seconds = uptime_seconds % 60

        uptime_message = f"Bot đã hoạt động được {days} ngày, {hours} giờ, {minutes} phút, {seconds} giây."
        message_to_send = Message(text=uptime_message)

        # Lấy danh sách ảnh từ API
        image_list_url = "https://api-dowig.onrender.com/images/naughty"
        #image_list_url = "https://api-dowig.onrender.com/images/couple"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        def get_valid_image_url():
            # Lấy ảnh hợp lệ, không phải từ Imgur
            while True:
                response = requests.get(image_list_url, headers=headers)
                response.raise_for_status()
                json_data = response.json()

                if isinstance(json_data, dict) and 'url' in json_data:
                    image_url = json_data.get('url')
                elif isinstance(json_data, list):
                    image_url = random.choice(json_data)
                else:
                    raise Exception("Dữ liệu trả về không hợp lệ")

                # Kiểm tra nếu URL là Imgur, thì lấy link khác
                if "imgur.com" not in image_url:
                    return image_url
        
        # Lấy URL hợp lệ
        image_url = get_valid_image_url()

        # Gọi API để tải ảnh từ URL
        image_response = requests.get(image_url, headers=headers)
        image_response.raise_for_status()  # Kiểm tra nếu có lỗi xảy ra
        image_path = 'modules/cache/temp_image5.jpeg'
        
        # Lưu ảnh vào đường dẫn tạm thời
        with open(image_path, 'wb') as f:
            f.write(image_response.content)

        # Gửi ảnh tới người dùng
        if os.path.exists(image_path):
            client.sendLocalImage(
                image_path, 
                message=message_to_send,
                thread_id=thread_id,
                thread_type=thread_type,
                ttl=100000
            )
            # Xóa ảnh tạm sau khi gửi
            os.remove(image_path)
        else:
            raise Exception("Không thể lưu ảnh")
    
    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=30000)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=30000)

def get_tmii():
    return {
        'uptime': handle_uptime_command
    }
