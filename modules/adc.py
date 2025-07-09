import os
import requests
from config import *  # ADMIN là chuỗi các ID admin
from zlapi.models import Message

# Chuyển đổi chuỗi ADMIN thành danh sách các ID admin
ADMIN_IDS = [admin_id.strip() for admin_id in ADMIN.split(',')]  # Tách chuỗi và loại bỏ khoảng trắng

des = {
    'version': "1.0.1",
    'credits': "LAMDev",
    'description': "Áp dụng code all link raw"
}

# ✅ Kiểm tra quyền truy cập nhóm
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN_IDS:
        return False
    return True

# ✅ Kiểm tra nếu người dùng là admin (danh sách admin)
def is_admin(author_id):
    return str(author_id) in ADMIN_IDS  # Kiểm tra xem author_id có trong danh sách ADMIN_IDS không

def read_command_content(command_name):
    try:
        file_path = f"modules/{command_name}.py"
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return str(e)

def handle_adc_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    
    lenhcanlay = message.split()

    if len(lenhcanlay) < 2:
        error_message = Message(text="Vui lòng nhập tên lệnh cần lấy.")
        client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=30000)
        return

    command_name = lenhcanlay[1].strip()

    if not is_admin(author_id):
        response_message = "Chỉ admin mới được sử dụng lệnh này."
        message_to_send = Message(text=response_message)
        client.replyMessage(message_to_send, message_object, thread_id, thread_type, ttl=30000)
        return

    command_content = read_command_content(command_name)
    
    if command_content is None:
        response_message = f"Lệnh '{command_name}' không được tìm thấy trong các module."
        message_to_send = Message(text=response_message)
        client.replyMessage(message_to_send, message_object, thread_id, thread_type, ttl=30000)
        return

    try:
        data = {
            "status": 200,
            "content": command_content,
            "content_type": "application/json",
            "charset": "UTF-8",
            "secret": "Kaito Kid",
            "expiration": "never"
        }

        response = requests.post("https://api.mocky.io/api/mock", json=data)
        response_data = response.json()

        mock_url = response_data.get("link")

        if mock_url:
            response_message = f"Thành công ✅\nDưới đây là link runmocky của modun lệnh {command_name}\nLink: {mock_url}"
        else:
            response_message = "Không thể tạo link run.mocky."

    except Exception as e:
        response_message = f"Có lỗi xảy ra: {str(e)}"

    message_to_send = Message(text=response_message)
    client.replyMessage(message_to_send, message_object, thread_id, thread_type, ttl=60000)

def get_tmii():
    return {
        'adc': handle_adc_command
    }
