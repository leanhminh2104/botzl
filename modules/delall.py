from zlapi.models import *
from zlapi import Message, ThreadType
from config import *

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
def handle_go_command(message, message_object, thread_id, thread_type, author_id, client, ttl=30000):
    if not check_group_access(thread_id, author_id):
        return
    if author_id not in ADMIN:
        noquyen = "Bạn không có quyền để thực hiện điều này!"
        client.replyMessage(Message(text=noquyen), message_object, thread_id, thread_type, ttl=30000)
        return

    num_to_delete = 100

    try:
        group_data = client.getRecentGroup(thread_id)

        if not group_data or not hasattr(group_data, 'groupMsgs'):
            client.replyMessage(Message(text="Không có tin nhắn nào để xóa!"), message_object, thread_id, thread_type, ttl=30000)
            return
        
        messages_to_delete = group_data.groupMsgs
        
        if not messages_to_delete:
            client.replyMessage(Message(text="Không có tin nhắn nào để xóa!"), message_object, thread_id, thread_type, ttl=30000)
            return

    except Exception as e:
        client.replyMessage(Message(text=f"Lỗi khi lấy tin nhắn: {str(e)}"), message_object, thread_id, thread_type, ttl=30000)
        return

    if len(messages_to_delete) < num_to_delete:
        client.replyMessage(Message(text=f"Chỉ có {len(messages_to_delete)} tin nhắn để xóa."), message_object, thread_id, thread_type, ttl=30000)
        num_to_delete = len(messages_to_delete)

    deleted_count = 0
    failed_count = 0

    for i in range(num_to_delete):
        msg = messages_to_delete[-(i + 1)]

        user_id = str(msg['uidFrom']) if msg['uidFrom'] != '0' else author_id
        try:
            deleted_msg = client.deleteGroupMsg(msg['msgId'], user_id, msg['cliMsgId'], thread_id)
            if deleted_msg.status == 0:
                deleted_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            continue

    if failed_count > 0:
        client.replyMessage(
            Message(text=f"Đã xóa {deleted_count} tin nhắn. Không thể xóa {failed_count} tin nhắn."),
            message_object, thread_id, thread_type, ttl=30000
        )
    else:
        client.replyMessage(Message(text=f"Đã xóa {deleted_count} tin nhắn thành công!"), message_object, thread_id, thread_type, ttl=30000)

def get_tmii():
    return {
        'delall': handle_go_command
    }