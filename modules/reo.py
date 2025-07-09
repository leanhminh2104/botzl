from zlapi.models import *
import os
import time
import threading
from zlapi.models import MultiMsgStyle, Mention, MessageStyle
from config import *

is_reo_running = False

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "Spamtag"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def off_reo(client, message_object, thread_id, thread_type):
    global is_reo_running
    is_reo_running = False
    client.replyMessage(Message(text="Đã dừng réo tên."), message_object, thread_id, thread_type,ttl=60000)

def handle_reo_command(message, message_object, thread_id, thread_type, author_id, client):
    global is_reo_running
    if not check_group_access(thread_id, author_id):
        return

    if author_id not in ADMIN:
        client.replyMessage(
            Message(text="Bạn không có quyền sử dụng"),
            message_object, thread_id, thread_type,ttl=60000
        )
        return

    command_parts = message.split()
    if len(command_parts) < 2:
        client.replyMessage(Message(text="Vui lòng chỉ định lệnh hợp lệ (vd: reo on hoặc reo off)."), message_object, thread_id, thread_type,ttl=60000)
        return

    action = command_parts[1].lower()

    if action == "off":
        if not is_reo_running:
            client.replyMessage(
                Message(text="⚠️ **Réo tên đã dừng lại.**"),
                message_object, thread_id, thread_type,tll=60000
            )
        else:
            off_reo(client, message_object, thread_id, thread_type)
        return

    if action != "on":
        client.replyMessage(Message(text="Vui lòng chỉ định lệnh 'on' hoặc 'off'."), message_object, thread_id, thread_type,ttl=60000)
        return

    if message_object.mentions:
        tagged_users = message_object.mentions[0]['uid']
    else:
        client.replyMessage(Message(text="Tag con chó cần ửa"), message_object, thread_id, thread_type, ttl=30000)
        return

    try:
        with open("noidung.txt", "r", encoding="utf-8") as file:
            Ngon = file.readlines()
    except FileNotFoundError:
        client.replyMessage(
            Message(text="Không tìm thấy file noidung.txt."),
            message_object,
            thread_id,
            thread_type,
            ttl=5000
        )
        return

    if not Ngon:
        client.replyMessage(
            Message(text="File noidung.txt không có nội dung nào để gửi."),
            message_object,
            thread_id,
            thread_type,
            ttl=12000
        )
        return

    is_reo_running = True
    def reo_loop():
        while is_reo_running:
            for noidung in Ngon:
                if not is_reo_running:
                    break
                mention = Mention(tagged_users, length=0, offset=0)
                client.send(Message(text=f" {noidung}", mention=mention), thread_id, thread_type,ttl=6000)
                time.sleep(2)

    reo_thread = threading.Thread(target=reo_loop)
    reo_thread.start()

def get_tmii():
    return {
        'reo': handle_reo_command
    }
