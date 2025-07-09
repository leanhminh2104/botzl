from zlapi.models import Message
import requests
import os
from config import *

des = {
    'version': "1.0.3",
    'credits': "LAMDev",
    'description': "Gửi ảnh anime ngẫu nhiên từ nhiều API"
}

# Danh sách nhiều API
API_URL_LIST = [
    "https://api-dowig.onrender.com/images/anime",
    "https://api.sumiproject.net/images/anime",
    "https://api-dowig.onrender.com/images/gura",
    "https://api-dowig.onrender.com/images/itachi"
    "https://api-dowig.onrender.com/images/mirai"
]

# Loại bỏ kiểm tra nhóm và admin, cho phép mọi người đều có thể sử dụng
def handle_anhgai_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        retries = 3  # Thử lại tối đa 3 lần cho mỗi API
        for api_url in API_URL_LIST:
            for attempt in range(retries):
                try:
                    # Gọi API và lấy dữ liệu ảnh
                    response = requests.get(api_url, timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    image_url = data.get('url')

                    if image_url:
                        # Tải ảnh từ URL và lưu vào file tạm
                        image_response = requests.get(image_url)
                        image_path = 'temp_image.jpeg'

                        with open(image_path, 'wb') as f:
                            f.write(image_response.content)

                        # Gửi ảnh với TTL
                        client.sendLocalImage(
                            image_path, 
                            thread_id=thread_id,
                            thread_type=thread_type,
                            width=1200,
                            height=1600,
                            message=Message(text="🖼️ Ảnh anime cho bạn nè! 💖"),
                            ttl=60000  # Thêm ttl vào đây
                        )

                        # Xóa file tạm sau khi gửi
                        os.remove(image_path)
                        return  # Nếu thành công thì thoát khỏi vòng lặp

                except requests.exceptions.RequestException as e:
                    # Nếu API bị lỗi, thử lại API khác
                    if attempt == retries - 1:
                        continue
                    else:
                        continue

        # Nếu tất cả các API đều bị lỗi
        error_message = Message(text="❌ Không thể lấy ảnh từ bất kỳ API nào.")
        client.sendMessage(error_message, thread_id, thread_type, ttl=30000)

    except Exception as e:
        # Lỗi chung khi không xử lý được
        error_message = Message(text=f"❌ Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=30000)

def get_tmii():
    return {
        'anhanime': handle_anhgai_command
    }
