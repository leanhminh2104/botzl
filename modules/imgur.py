import requests
from zlapi.models import Message
import json
from config import *

des = {
    'version': "1.0.0",
    'credits': "DuongNgocc",
    'description': "UpLoad ảnh hoặc video lên imgur"
}

IMGUR_CLIENT_ID = "85a847235508ec9" 
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_upload_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    try:
        if hasattr(message_object, 'msgType') and message_object.msgType in ["chat.photo", "chat.video"]:
            media_url = message_object.content.get('href', '').replace("\\/", "/")
            if not media_url:
                send_error_message("Không tìm thấy liên kết ảnh/video.", thread_id, thread_type, client)
                return

            imgur_link = upload_to_imgur(media_url)
            if imgur_link:
                send_success_message(f"Thành Công: {imgur_link}", thread_id, thread_type, client)
            else:
                send_error_message("Lỗi khi upload ảnh/video lên Imgur.", thread_id, thread_type, client)

        elif getattr(message_object, 'quote', None):
            attach = getattr(message_object.quote, 'attach', None)
            if attach:
                try:
                    attach_data = json.loads(attach)
                except json.JSONDecodeError:
                    send_error_message("Phân tích JSON thất bại.", thread_id, thread_type, client)
                    return

                media_url = attach_data.get('hdUrl') or attach_data.get('href')
                if media_url:
                    imgur_link = upload_to_imgur(media_url)
                    if imgur_link:
                        send_success_message(f"Ảnh/video đã được upload: {imgur_link}", thread_id, thread_type, client)
                    else:
                        send_error_message("Lỗi khi upload ảnh/video lên Imgur.", thread_id, thread_type, client)
                else:
                    send_error_message("Không tìm thấy liên kết trong file đính kèm.", thread_id, thread_type, client)
            else:
                send_error_message("Không tìm thấy file đính kèm.", thread_id, thread_type, client)
        else:
            send_error_message("Vui lòng gửi ảnh/video hoặc phản hồi file đính kèm.", thread_id, thread_type, client)
    except Exception as e:
        print(f"Lỗi khi xử lý lệnh upload: {str(e)}")
        send_error_message("Đã xảy ra lỗi khi xử lý lệnh.", thread_id, thread_type, client)

def upload_to_imgur(media_url):
    api_url = "https://api.imgur.com/3/image"
    headers = {
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
    }
    data = {
        "image": media_url,
        "type": "url"
    }

    try:
        response = requests.post(api_url, headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Phản hồi từ API Imgur: {result}")
            return result.get('data', {}).get('link')
        else:
            print(f"Lỗi API Imgur: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Lỗi khi gọi API Imgur: {str(e)}")
        return None

def send_success_message(message, thread_id, thread_type, client):
    success_message = Message(text=message)
    try:
        client.send(success_message, thread_id, thread_type)
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn thành công: {str(e)}")

def send_error_message(message, thread_id, thread_type, client):
    error_message = Message(text=message)
    try:
        client.send(error_message, thread_id, thread_type)
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn lỗi: {str(e)}")

def get_tmii():
    return {
        'imgur': handle_upload_command
    }
