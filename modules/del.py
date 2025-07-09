from zlapi.models import Message, MultiMsgStyle, MessageStyle
from config import *
ADMIN_ID = ADMIN

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "Xoá tin nhắn người dùng"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_del_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    if author_id not in ADMIN:
        msg = "• Bạn Không Có Quyền! Chỉ có admin mới có thể sử dụng lệnh này."
        styles = MultiMsgStyle([
            MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
            MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
            MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
        ])
        client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type, ttl=30000)
        return

    if message_object.quote:
        msg2del = message_object.quote
        user_id = str(msg2del.ownerId)
    else:
        msg = f" • Không thể xoá tin nhắn vì cú pháp không hợp lệ!\n\n| Command: {PREFIX}del <reply tin nhắn cần xoá>"
        styles = MultiMsgStyle([
            MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
            MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
            MessageStyle(offset=msg.find("Command:"), length=11, style="bold", auto_format=False),
            MessageStyle(offset=msg.find("Command:"), length=1, style="color", color="#585b70", auto_format=False),
            MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
        ])
        client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type, ttl=30000)
        return

    deleted_msg = client.deleteGroupMsg(msg2del.globalMsgId, user_id, msg2del.cliMsgId, thread_id)
    if deleted_msg.status == 0:
        msg = "• Đã xoá tin nhắn của người dùng được reply."
        styles = MultiMsgStyle([
            MessageStyle(offset=0, length=2, style="color", color="#a6e3a1", auto_format=False),
            MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
            MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
        ])
        client.send(Message(text=msg, style=styles), thread_id, thread_type, ttl=30000)
    else:
        msg = "• Bot không thể xoá tin nhắn vì không có quyền! Vui lòng cấp quyền cho bot để thực hiện thao tác này."
        styles = MultiMsgStyle([
            MessageStyle(offset=0, length=2, style="color", color="#fab387", auto_format=False),
            MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
            MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
        ])
        client.send(Message(text=msg, style=styles), thread_id, thread_type, ttl=30000)

def get_tmii():
    return {
        'del': handle_del_command
    }
