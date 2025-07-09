from zlapi.models import Message
import requests
import os
from config import *

des = {
    'version': "1.0.2",
    'credits': "DuongNgoc",
    'description': "Gửi ảnh meme hài"
}

# Xử lý lệnh gửi ảnh meme hài
def handle_anhgai_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        # Lấy dữ liệu ảnh meme từ API
        url = "https://api-dowig.onrender.com//images/meme"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        thinh = data.get('data', 'Không có dữ liệu ảnh meme')

        # Thông điệp gửi kèm
        sendmess = f"{thinh}"
        message_to_send = Message(text=sendmess)

        # Tải ảnh meme
        image_url = data['url']
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # Lưu ảnh vào tệp tạm thời
        image_path = 'temp_image.jpeg'
        with open(image_path, 'wb') as f:
            f.write(image_response.content)

        # Gửi ảnh với TTL (Time to live)
        ttl = 100000  # Thời gian sống của ảnh, có thể điều chỉnh theo nhu cầu
        client.sendLocalImage(
            image_path, 
            thread_id=thread_id,
            thread_type=thread_type,
            width=1200,
            height=1600,
            message=Message(text="🖼️ Ảnh meme cho bạn nè! 💖"),
            ttl=ttl  # Thêm TTL vào ảnh
        )

        # Xóa tệp ảnh sau khi gửi
        os.remove(image_path)

    except requests.exceptions.RequestException as e:
        # Gửi thông báo lỗi nếu có vấn đề khi gọi API
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=10000)  # Giữ TTL cho thông báo lỗi

    except Exception as e:
        # Gửi thông báo lỗi nếu có lỗi khác
        error_message = Message(text=f"Lỗi khi xử lý ảnh: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=10000)  # Giữ TTL cho thông báo lỗi

def get_tmii():
    return {
        'meme': handle_anhgai_command
    }
