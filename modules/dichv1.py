from zlapi.models import Message
import json
import urllib.parse
import os
import requests
from io import BytesIO
from PIL import Image

des = {
    'version': "1.0.0",
    'credits': "Tai sex",
    'description': "Tạo sticker khi reply vào một ảnh"
}

TEMP_IMAGE = "temp_image"
TEMP_WEBP = "temp_image.webp"

def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):
    if not message_object.quote:
        client.sendMessage(
            Message(text="Hãy reply vào ảnh cần tạo sticker."),
            thread_id=thread_id,
            thread_type=thread_type
        )
        return

    attach = message_object.quote.attach
    if not attach:
        client.sendMessage(
            Message(text="Không có ảnh nào được reply."),
            thread_id=thread_id,
            thread_type=thread_type
        )
        return

    try:
        attach_data = json.loads(attach)
        image_url = attach_data.get('hdUrl') or attach_data.get('href')
    except (json.JSONDecodeError, TypeError):
        image_url = attach

    if not image_url:
        client.sendMessage(
            Message(text="Không tìm thấy URL ảnh."),
            thread_id=thread_id,
            thread_type=thread_type
        )
        return

    image_url = image_url.replace("\\/", "/")
    image_url = urllib.parse.unquote(image_url)

    if not is_valid_image_url(image_url):
        client.sendMessage(
            Message(text="URL không phải là ảnh hợp lệ."),
            thread_id=thread_id,
            thread_type=thread_type
        )
        return

    # Tải ảnh gốc về
    try:
        resp = requests.get(image_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        client.sendMessage(
            Message(text=f"Lỗi tải ảnh gốc: {str(e)}"),
            thread_id=thread_id,
            thread_type=thread_type
        )
        return

    # Lưu ảnh gốc tạm thời
    with open(TEMP_IMAGE, 'wb') as f:
        f.write(resp.content)

    # Chuyển đổi ảnh sang webp
    try:
        img = Image.open(TEMP_IMAGE).convert("RGBA")
        img.save(TEMP_WEBP, format="WEBP")
    except Exception as e:
        client.sendMessage(
            Message(text=f"Lỗi chuyển ảnh sang webp: {str(e)}"),
            thread_id=thread_id,
            thread_type=thread_type
        )
        cleanup_temp_files()
        return

    # Upload ảnh webp lên catbox.moe (hoặc thay bằng dịch vụ khác nếu cần)
    webp_url = upload_to_catbox(TEMP_WEBP)
    if not webp_url:
        client.sendMessage(
            Message(text="Không thể upload ảnh webp lên server."),
            thread_id=thread_id,
            thread_type=thread_type
        )
        cleanup_temp_files()
        return

    # Gửi sticker
    try:
        client.send_custom_sticker(
            animationImgUrl=webp_url,
            staticImgUrl=webp_url,
            thread_id=thread_id,
            thread_type=thread_type,
            reply=message_object,
            width=None,
            height=None
        )
        client.sendMessage(
            Message(text="Sticker đã được tạo!"),
            thread_id=thread_id,
            thread_type=thread_type
        )
    except Exception as e:
        client.sendMessage(
            Message(text=f"Lỗi gửi sticker: {str(e)}"),
            thread_id=thread_id,
            thread_type=thread_type
        )

    # Xóa file tạm
    cleanup_temp_files()

def is_valid_image_url(url):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    return any(url.lower().endswith(ext) for ext in valid_extensions)

def upload_to_catbox(file_path):
    """
    Upload file ảnh lên catbox.moe miễn phí, trả về URL ảnh nếu thành công.
    """
    try:
        with open(file_path, 'rb') as f:
            files = {'fileToUpload': f}
            response = requests.post("https://catbox.moe/user/api.php", data={'reqtype':'fileupload'}, files=files, timeout=15)
            response.raise_for_status()
            url = response.text.strip()
            if url.startswith("http"):
                return url
            else:
                return None
    except:
        return None

def cleanup_temp_files():
    for f in [TEMP_IMAGE, TEMP_WEBP]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass

def get_tmii():
    return {
        'stkv3': handle_stk_command
    }
