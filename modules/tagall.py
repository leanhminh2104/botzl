from zlapi.models import Message, Mention, MultiMsgStyle, MessageStyle
from config import *
import time

ADMIN_ID = ADMIN

des = {
    'version': "1.0.1",
    'credits': "DuongNgocc",
    'description': "Tag tên thành viên trong nhóm"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def is_admin(author_id):
    return author_id == ADMIN_ID

def handle_checkid_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    try:

        group_info = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]

        creator_id = group_info.get('creatorId')
        admin_ids = group_info.get('adminIds', [])

        if admin_ids is None:
            admin_ids = []

        all_admin_ids = set(admin_ids)
        all_admin_ids.add(creator_id)
        all_admin_ids.update(ADMIN)

        if author_id not in all_admin_ids and author_id not in ADMIN:
            msg = "• Bạn Không Có Quyền! Chỉ có admin mới có thể sử dụng được lệnh này."
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
                MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
                MessageStyle(offset=0, length=len(msg), style="font", size="11", auto_format=False)
            ])
       
            
            client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type,ttl=20000)
            return

        data = client.fetchGroupInfo(groupId=thread_id)
        members = data['gridInfoMap'][str(thread_id)]['memVerList']
        
        messages = []
        for mem in members:
            user_id = mem.split('_')[0]
            user_name = mem.split('_')[1]  
            mention = Mention(uid=user_id, offset=0, length=len(user_name))
            messages.append(Message(text=f" {user_name}", mention=mention))

        for msg in messages:
            client.send(msg, thread_id=thread_id, thread_type=thread_type)
            time.sleep(0.3)

    except Exception as e:
        error_message = f"lỗi clmm: {str(e)}"
        client.send(Message(text=error_message), thread_id=thread_id, thread_type=thread_type)

def get_tmii():
    return {
        'tagall': handle_checkid_command
    }
