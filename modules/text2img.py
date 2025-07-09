from zlapi.models import Message
import requests
import urllib.parse
import os
from config import *

des = {
    'version': "1.9.2",
    'credits': "LAMDev",
    'description': "Tạo ảnh từ text"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_text2img_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    text = message.split()

    if len(text) < 2 or not text[1].strip():
        error_message = Message(text="Vui lòng nhập nội dung hợp lệ để chuyển đổi thành ảnh.")
        client.replyMessage(error_message, message_object, thread_id, thread_type)
        return

    content = " ".join(text[1:])
    encoded_text = urllib.parse.quote(content, safe='')

    try:
        apianh = f'http://www.hungdev.id.vn/ai/text2img?apiKey=12345&query={encoded_text}'
        response = requests.get(apianh)
        response.raise_for_status()

        data = response.json()
        links = data.get('data', [])

        if len(links) < 2:
            error_message = Message(text="API không trả về đủ ảnh.")
            client.sendMessage(error_message, thread_id, thread_type)
            return

        image_paths = []
        for idx, link in enumerate(links):
            if link:
                image_response = requests.get(link)
                image_path = f'modules/cache/temp_image_{idx}.jpeg'
                
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                
                image_paths.append(image_path)

        if image_paths:
            for image_path in image_paths:
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
        'timg': handle_text2img_command
    }
