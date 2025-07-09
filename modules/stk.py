from zlapi.models import Message
import json
import urllib.parse
import os
import requests
from PIL import Image
from io import BytesIO
from zlapi.models import Message, MultiMsgStyle, MessageStyle
from zlapi._threads import ThreadType
from config import *

des = {
    'version': "1.0.3",
    'credits': "LAMDev",
    'description': "Tạo sticker khi reply vào một ảnh"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    if message_object.quote:
        attach = message_object.quote.attach
        if attach:
            try:
                attach_data = json.loads(attach)
            except json.JSONDecodeError:
                client.sendMessage(
                    Message(text="❌ Dữ liệu ảnh không hợp lệ."),
                    thread_id=thread_id,
                    thread_type=thread_type,
                    ttl=60000
                )
                return

            image_url = attach_data.get('hdUrl') or attach_data.get('href')
            if not image_url:
                client.sendMessage(
                    Message(text="❌ Không tìm thấy URL ảnh."),
                    thread_id=thread_id,
                    thread_type=thread_type,
                    ttl=60000
                )
                return

            image_url = image_url.replace("\\/", "/")
            image_url = urllib.parse.unquote(image_url)

            if is_valid_image_url(image_url):
                webp_image_url = convert_to_webp_and_upload(image_url)
                if webp_image_url:
                    # Gửi sticker đã chuyển đổi
                    client.sendCustomSticker(
                        animationImgUrl=webp_image_url,
                        staticImgUrl=webp_image_url,
                        thread_id=thread_id,
                        thread_type=thread_type,
                        reply=message_object,
                        width=None,
                        height=None,
                        ttl=2592000
                    )
                    # Gửi thông báo thành công
                    send_message = "✅ Đã tạo Sticker [ V1 ] thành công !"
                    style = MultiMsgStyle([
                        MessageStyle(offset=0, length=len(send_message), style="font", size="10", auto_format=False),
                        MessageStyle(offset=0, length=len(send_message), style="bold", auto_format=False)
                    ])
                    styled_message = Message(text=send_message, style=style)
                    client.replyMessage(styled_message, message_object, thread_id, thread_type, ttl=30000)
                else:
                    client.sendMessage(
                        Message(text="❌ Hình ảnh không hợp lệ, không thể chuyển đổi."),
                        thread_id=thread_id, 
                        thread_type=thread_type,
                        ttl=60000
                    )
            else:
                client.sendMessage(
                    Message(text="❌ URL không phải là ảnh hợp lệ."),
                    thread_id=thread_id, 
                    thread_type=thread_type,
                    ttl=60000
                )
        else:
            client.sendMessage(
                Message(text="❌ Không có ảnh nào được reply."),
                thread_id=thread_id, 
                thread_type=thread_type,
                ttl=60000
            )
    else:
        client.sendMessage(
            Message(text="❌ Hãy reply vào ảnh cần tạo sticker."),
            thread_id=thread_id, 
            thread_type=thread_type,
            ttl=60000
        )

def is_valid_image_url(url):
    valid_extensions = ['.jpg', '.mp4', '.jpeg', '.png', '.gif']
    return any(url.lower().endswith(ext) for ext in valid_extensions)

def convert_to_webp_and_upload(image_url):
    """ Tải ảnh về, chuyển sang WebP, rồi upload lên server ảnh """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # Mở ảnh bằng PIL
        img = Image.open(BytesIO(response.content))
        webp_io = BytesIO()
        img.save(webp_io, format="WEBP", quality=80)  # Chuyển đổi sang WebP
        webp_io.seek(0)

        # Upload ảnh lên catbox.moe để lấy URL
        files = {'fileToUpload': ('sticker.webp', webp_io, 'image/webp')}
        upload_response = requests.post("https://catbox.moe/user/api.php", 
                                        files=files, 
                                        data={"reqtype": "fileupload"})
        
        # Nếu upload thành công, lấy URL của ảnh
        if upload_response.status_code == 200:
            return upload_response.text.strip()
        return None

    except Exception as e:
        print(f"❌ Lỗi khi chuyển ảnh sang WebP: {e}")
        return None

def get_tmii():
    return {
        'stk': handle_stk_command
    }
