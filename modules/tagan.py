from zlapi.models import Message, Mention
from config import *

des = {
    'version': "1.0.0",
    'credits': "DuongNgocc",
    'description': "Thông báo cho nhóm"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_tagall_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    if author_id not in ADMIN:
        client.replyMessage(
            Message(text="🚫 403 Dương Ngọc Mới Được Xài Em Nhá"),
            message_object, thread_id, thread_type
        )
        return

    noidung = message.split()
    
    if len(noidung) < 2:
        error_message = Message(text="MÀY KHÔNG NHẬP NỘI DUNG BỐ TAO CŨNG KHÔNG LÀM ĐƯỢC.")
        client.sendMessage(error_message, thread_id, thread_type)
        return

    noidung1 = " ".join(noidung[1:])

    content = "‎" + noidung1 
    mention = Mention("-1", length=len(content) + 1, offset=1)
    client.replyMessage(
        Message(
            text=content, mention=mention
        ),
        message_object,
        thread_id=thread_id,
        thread_type=thread_type
    )

def get_tmii():
    return {
        'tagan': handle_tagall_command
    }