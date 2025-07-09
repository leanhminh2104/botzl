from zlapi.models import Message, ThreadType
from config import *

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "Lấy danh thiếp người dùng hoặc danh thiếp người được tag"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_cardinfo_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    userId = message_object.mentions[0]['uid'] if message_object.mentions else author_id
    
    if not userId:
        client.send(
            Message(text="Không tìm thấy người dùng."),
            thread_id=thread_id,
            thread_type=thread_type
        )
        return
    
    
    user_info = client.fetchUserInfo(userId).changed_profiles.get(userId)
    
    if not user_info:
        client.send(
            Message(text="Không thể lấy thông tin người dùng."),
            thread_id=thread_id,
            thread_type=thread_type
        )
        return
    
    avatarUrl = user_info.avatar
    
    if not avatarUrl:
        client.send(
            Message(text="Người dùng này không có ảnh đại diện."),
            thread_id=thread_id,
            thread_type=thread_type
        )
        return
    
    client.sendBusinessCard(userId=userId, qrCodeUrl=avatarUrl, thread_id=thread_id, thread_type=thread_type)

def get_tmii():
    return {
        'cardinfo': handle_cardinfo_command
    }
