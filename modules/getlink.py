from zlapi.models import Message
import json
import urllib.parse
from config import *

des = {
    'version': "1.0.0",
    'credits': "LAMDev",
    'description': "Getlink hình ảnh, file, gif, link, video"
}

last_sent_image_url = None  
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_getlink_command(message, message_object, thread_id, thread_type, author_id, client):
    global last_sent_image_url
    if not check_group_access(thread_id, author_id):
        return
    msg_obj = message_object

    if msg_obj.msgType == "chat.photo":
        img_url = msg_obj.content.href.replace("\\/", "/")
        img_url = urllib.parse.unquote(img_url)
        last_sent_image_url = img_url
        send_image_link(img_url, thread_id, thread_type, client)

    elif msg_obj.quote:
        attach = msg_obj.quote.attach
        if attach:
            try:
                attach_data = json.loads(attach)
            except json.JSONDecodeError as e:
                print(f"Lỗi khi phân tích JSON: {str(e)}")
                return

            image_url = attach_data.get('hdUrl') or attach_data.get('href')
            if image_url:
                send_image_link(image_url, thread_id, thread_type, client)
            else:
                send_error_message(thread_id, thread_type, client)
        else:
            send_error_message(thread_id, thread_type, client)
    else:
        send_error_message(thread_id, thread_type, client)

def send_image_link(image_url, thread_id, thread_type, client):
    if image_url:
        message_to_send = Message(text=f"Link của bạn đây\n{image_url}")
        
        if hasattr(client, 'send'):
            client.send(message_to_send, thread_id, thread_type, ttl=300000)
        else:
            print("Client không hỗ trợ gửi tin nhắn.")

def send_error_message(thread_id, thread_type, client):
    error_message = Message(text="Vui lòng reply(phản hồi) hình ảnh, gif, file, video cần getlink.")
    
    if hasattr(client, 'send'):
        client.send(error_message, thread_id, thread_type, ttl=3000)
    else:
        print("Client không hỗ trợ gửi tin nhắn.")

def get_tmii():
    return {
        'getlink': handle_getlink_command
    }