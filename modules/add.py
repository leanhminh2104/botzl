from zlapi.models import Message, MultiMsgStyle, MessageStyle
from config import *
ADMIN_ID = ADMIN
import time

des = {
    'version': "1.0.3",
    'credits': "LAMDev",
    'description': "Thêm thành viên vào nhóm bằng UID hoặc số điện thoại."
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")

def handle_adduser_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    if author_id not in ADMIN:
        msg = "• Bạn Không Có Quyền! Chỉ có admin mới có thể sử dụng được lệnh này."
        styles = MultiMsgStyle([ 
            MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
            MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
            MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
        ])
        client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type, ttl=20000)
        return

    text = message.split()
    if len(text) < 2:
        error_message = Message(text="Vui lòng nhập UID hoặc số điện thoại người dùng cần thêm vào nhóm.")
        client.sendMessage(error_message, thread_id, thread_type, ttl=20000)
        return

    content = text[1]

    if content.isdigit() and (len(content) == 10 or len(content) == 11):
        phone_number = content
        try:
            user_info = client.fetchPhoneNumber(phone_number)

            if user_info and hasattr(user_info, 'uid'):
                user_id = user_info.uid
                user_name = user_info.zalo_name

                client.addUsersToGroup(user_id, thread_id)

                send_message = f"Thêm thành công {user_name} vào nhóm."
            else:
                send_message = "Không tìm thấy người dùng với số điện thoại này."

        except Exception as e:
            send_message = f"Lỗi khi thêm người dùng từ số điện thoại: {str(e)}"
    
    else:
        formatted_user_id = f"{content}_0"

        try:
            client.addUsersToGroup(content, thread_id)

            time.sleep(1)

            author_info = client.fetchUserInfo(formatted_user_id)

            if isinstance(author_info, dict) and 'changed_profiles' in author_info:
                user_data = author_info['changed_profiles'].get(content, {})
                author_name = user_data.get('zaloName', 'Không rõ tên.')

                send_message = f"Thêm thành công {author_name} vào nhóm."
            else:
                send_message = "Thêm được nhưng không lấy được thông tin."

        except Exception as e:
            send_message = f"Lỗi khi thêm người dùng từ UID: {str(e)}"

    gui = Message(text=send_message)
    client.sendMessage(gui, thread_id, thread_type, ttl=20000)

def get_tmii():
    return {
        'add': handle_adduser_command
    }
