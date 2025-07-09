from zlapi import ZaloAPI
from zlapi.models import *
from config import *

des = {
    'version': "1.0.1",
    'credits': "LAMDev",
    'description': "xem id bản thân."
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_meid_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    user_id = author_id

    response_message = f"{user_id}"

    message_to_send = Message(text=response_message)

    client.replyMessage(message_to_send, message_object, thread_id, thread_type)
    
def get_tmii():
    return {
        'in4': handle_meid_command
    }
