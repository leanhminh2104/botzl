from zlapi.models import Message
from config import *
import time

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "addid <uid member cần tag>"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  

def handle_adduser_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    
    text = message.split()

    if len(text) < 2:
        client.sendMessage(Message(text="Vui lòng nhập ID người dùng cần thêm vào nhóm."), thread_id, thread_type, ttl=30000)
        return

    content = text[1]

    # Kiểm tra xem ID người dùng có phải là số không
    if not content.isdigit():
        client.sendMessage(Message(text="ID người dùng phải là số."), thread_id, thread_type, ttl=30000)
        return

    formatted_user_id = f"{content}_0"

    try:
        # Thêm người vào nhóm
        client.addUsersToGroup(content, thread_id)

        time.sleep(1)

        author_info = client.fetchUserInfo(formatted_user_id)

        if isinstance(author_info, dict) and 'changed_profiles' in author_info:
            user_data = author_info['changed_profiles'].get(content, {})
            author_name = user_data.get('zaloName', 'Chưa rõ tên')

            send_message = f"Mời thành công {author_name} vào nhóm."
        else:
            send_message = "Lỗi thông tin hoặc ID không hợp lệ."

    except Exception as e:
        send_message = f"❌ Lỗi: {str(e)}"

    client.sendMessage(Message(text=send_message), thread_id, thread_type, ttl=30000)

def get_tmii():
    return {
        'addid': handle_adduser_command
    }
