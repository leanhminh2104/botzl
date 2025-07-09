import sys,os
from config import *
ADMIN_ID = ADMIN
from zlapi.models import Message, MultiMsgStyle, MessageStyle

des = {
    'version': "1.0.0",
    'credits': "DuongNgocc",
    'description': "reset lai bot"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def is_admin(author_id):
    return author_id == ADMIN_ID
def handle_reset_command(message, message_object, thread_id, thread_type, author_id, client):
   # if hasattr(message_object, 'content') and isinstance(message_object.content, str):
    if not check_group_access(thread_id, author_id):
        return

    if author_id not in ADMIN:
				
            msg = "• Bạn Không Có Quyền! Chỉ có admin mới có thể sử dụng được lệnh này."
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
                MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
                MessageStyle(offset=0, length=len(msg), style="font", size="11", auto_format=False)
            ])
       
            
            client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type,ttl=20000)
            return
    msg = f"•Bắt Đầu Reset! \n• Please Wait 1 -> 5 seconds"
    styles = MultiMsgStyle([
    MessageStyle(offset=0, length=2, style="color", color="#a24ffb", auto_format=False),
    MessageStyle(offset=2, length=len(msg)-2, style="color", color="#ffaf00", auto_format=False),
    MessageStyle(offset=0, length=40, style="color", color="#a24ffb", auto_format=False),
    MessageStyle(offset=45, length=len(msg)-2, style="color", color="#ffaf00", auto_format=False),
    MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
])
    
    client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type,ttl=20000)
    success_msg = "• Reset Thành Công!"
    success_styles = MultiMsgStyle([
        MessageStyle(offset=0, length=len(success_msg), style="color", color="#00ff00", auto_format=False),
        MessageStyle(offset=0, length=len(success_msg), style="font", size="13", auto_format=False)
    ])
    client.replyMessage(Message(text=success_msg, style=success_styles), message_object, thread_id, thread_type, ttl=20000)
    python = sys.executable
    os.execl(python, python, *sys.argv)
    
def get_tmii():
    return {
        'rs': handle_reset_command
    }
