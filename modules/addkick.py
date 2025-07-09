from zlapi.models import Message
from config import *
import time

des = {
    'version': "1.2.0",
    'credits': "LAMDev",
    'description': "Add va Kick"
}

def check_group_access(thread_id, sender_id):
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")  # Đưa print lên trước return
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  

def handle_addkick_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    
    text = message.split()

    if len(text) < 3: 
        error_message = Message(text="Vui lòng sử dụng cú pháp: ..addkick @tag hoặc ..addkick <ID> <số lần lặp>.")
        client.sendMessage(error_message, thread_id, thread_type, ttl=30000)
        return

    user_id = None
    repeat_count = 1 

    if message_object.mentions:
        user_id = message_object.mentions[0]['uid']
    elif message_object.quote:
        user_id = str(message_object.quote.ownerId)
    else:
        user_id = text[1]
    
    try:
        repeat_count = int(text[2])
        if repeat_count < 1:
            repeat_count = 1
    except ValueError:
        client.sendMessage(Message(text="Số lần lặp không hợp lệ."), thread_id, thread_type, ttl=30000)
        return
    
    if author_id not in ADMIN:
        client.sendMessage(Message(text="Chỉ Admin mới được sử dụng lệnh này !"), thread_id, thread_type, ttl=30000)
        return
    
    for i in range(repeat_count):
        try:
            client.kickUsersInGroup(user_id, thread_id)
            send_message = f"Đã sút người dùng {user_id} khỏi nhóm."
            client.sendMessage(Message(text=send_message), thread_id, thread_type, ttl=30000)
        except Exception as e:
            client.sendMessage(Message(text=f"Lỗi khi sút người dùng: {str(e)}"), thread_id, thread_type, ttl=30000)
            return
        
        try:
            time.sleep(0.2)
            client.addUsersToGroup(user_id, thread_id)
            user_info = client.fetchUserInfo(user_id)
            if isinstance(user_info, dict) and 'changed_profiles' in user_info:
                user_data = user_info['changed_profiles'].get(user_id, {})
                user_name = user_data.get('zaloName', 'Không rõ tên.')
            else:
                user_name = "Người dùng không rõ tên."
            send_message = f"Đã thêm lại người dùng {user_name} vào nhóm."
            client.sendMessage(Message(text=send_message), thread_id, thread_type, ttl=30000)
        except Exception as e:
            client.sendMessage(Message(text=f"Lỗi khi thêm lại người dùng: {str(e)}"), thread_id, thread_type, ttl=30000)
            return

def get_tmii():
    return {
        'addkick': handle_addkick_command
    }
