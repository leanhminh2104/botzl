from zlapi.models import Message
from config import *
import time

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "add member by phone number <phone_number>"
}

def check_group_access(thread_id, sender_id):
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")  # Đưa print lên trước return
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  

def handle_adduser_by_phone_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    text = message.split()

    if len(text) < 2:
        error_message = Message(text="Nhập Sdt User Cần Add.")
        client.sendMessage(error_message, thread_id, thread_type, ttl=30000)
        return

    phone_number = text[1]

    try:
        user_info = client.fetchPhoneNumber(phone_number)

        print("Phản hồi zalo", user_info)

        if user_info and hasattr(user_info, 'uid'):
            user_id = user_info.uid
            user_name = user_info.zalo_name  

            client.addUsersToGroup(user_id, thread_id)

            send_message = f"Đã Add {user_name} Vào Nhóm."
        else:
            send_message = "Lỗi không thể tìm thấy người dùng với số điện thoại này."

    except Exception as e:
        send_message = f"Chưa Thể Thêm User: {str(e)}"

    gui = Message(text=send_message)
    client.sendMessage(gui, thread_id, thread_type, ttl=30000)

def get_tmii():
    return {
        'addsdt': handle_adduser_by_phone_command
    }
