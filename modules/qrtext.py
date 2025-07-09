from zlapi.models import Message
import requests
import urllib.parse
import os
from config import *

des = {
    'version': "1.9.2",
    'credits': "LAMDev",
    'description': "Tạo qrcode từ text"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_qrcode_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    text = message.split()

    if len(text) < 2 or not text[1].strip():
        error_message = Message(text="Vui lòng nhập nội dung muốn tạo qrcode.")
        client.replyMessage(error_message, message_object, thread_id, thread_type)
        return

    content = " ".join(text[1:])
    encoded_text = urllib.parse.quote(content, safe='')

    try:
        apiqrcode = f'https://api.qrserver.com/v1/create-qr-code/?size=4820x4820&data={encoded_text}'
        image_response = requests.get(apiqrcode)
        image_path = 'modules/cache/temp_image1.jpeg'
        with open(image_path, 'wb') as f:
            f.write(image_response.content)

        if os.path.exists(image_path):
                    client.sendLocalImage(
                        image_path, 
                        message=None,
                        thread_id=thread_id,
                        thread_type=thread_type,
                        width=1600,
                        height=1600
                    )
                    os.remove(image_path)

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except KeyError as e:
        error_message = Message(text=f"Dữ liệu từ API không đúng cấu trúc: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def get_tmii():
    return {
        'qrtext': handle_qrcode_command
    }
