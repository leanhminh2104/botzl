from zlapi.models import Message
import json
import urllib.parse
import cv2
import numpy as np
import requests
import logging
from config import *
import io
from PIL import Image

des = {
    'version': "1.5.0",
    'credits': "LAMDev",
    'description': "Làm nét hình ảnh gửi dạng img và link (không giới hạn, có giả trình duyệt)"
}

last_sent_image_url = None

# Headers giả trình duyệt
FAKE_BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.google.com/'
}

IMGUR_CLIENT_ID = 'f5494b2d26f43c2'

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        logging.info(f"Kiểm tra quyền truy cập: {sender_id} không phải admin trong nhóm {thread_id}")
        return False
    logging.info(f"Kiểm tra quyền truy cập: {sender_id} có quyền truy cập nhóm {thread_id}")
    return True

def handle_lamnet_command(message, message_object, thread_id, thread_type, author_id, client):
    global last_sent_image_url
    logging.info(f"Nhận lệnh từ {author_id} trong nhóm {thread_id}")

    if not check_group_access(thread_id, author_id):
        logging.info(f"{author_id} không có quyền trong nhóm {thread_id}, bỏ qua lệnh.")
        return

    msg_obj = message_object

    # Ảnh gửi trực tiếp
    if msg_obj.msgType == "chat.photo":
        img_url = urllib.parse.unquote(msg_obj.content.href.replace("\\/", "/"))
        last_sent_image_url = img_url
        logging.info(f"Ảnh gửi trực tiếp, URL: {img_url}")
        process_image_upscale(img_url, thread_id, thread_type, client)

    # Ảnh từ tin nhắn reply
    elif msg_obj.quote:
        attach = msg_obj.quote.attach
        if attach:
            try:
                attach_data = json.loads(attach)
                image_url = attach_data.get('hdUrl') or attach_data.get('href')
                if image_url:
                    last_sent_image_url = image_url
                    logging.info(f"Ảnh từ reply, URL: {image_url}")
                    process_image_upscale(image_url, thread_id, thread_type, client)
                    return
            except json.JSONDecodeError:
                logging.error(f"Lỗi khi giải mã dữ liệu attach: {attach}")
        send_error_message(thread_id, thread_type, client)

    else:
        send_error_message(thread_id, thread_type, client)

def process_image_upscale(image_url, thread_id, thread_type, client):
    if not image_url:
        logging.error(f"Không có URL ảnh.")
        send_error_message(thread_id, thread_type, client)
        return

    # Tải ảnh từ URL
    try:
        response = requests.get(image_url, headers=FAKE_BROWSER_HEADERS, timeout=60)
        response.raise_for_status()
        img_data = response.content
        img = Image.open(io.BytesIO(img_data))
        img = np.array(img)

        # Làm nét ảnh với OpenCV
        kernel = np.array([[-1, -1, -1],
                           [-1, 9, -1],
                           [-1, -1, -1]])  # Kernel làm nét
        sharpened_img = cv2.filter2D(img, -1, kernel)

        # Chuyển lại ảnh thành kiểu có thể gửi
        _, img_encoded = cv2.imencode('.jpeg', sharpened_img)
        img_bytes = img_encoded.tobytes()

        # Lưu lại ảnh đã làm nét tạm thời
        with open("anh_lamnet.jpeg", "wb") as f:
            f.write(img_bytes)

        # Gửi ảnh đã làm nét
        send_image_with_link(img_bytes, "anh_lamnet.jpeg", thread_id, thread_type, client)

    except Exception as e:
        logging.error(f"Lỗi khi xử lý ảnh: {e}")
        send_error_message(thread_id, thread_type, client, f"❌ Lỗi xử lý ảnh: {e}")

def send_image_with_link(image_data, file_name, thread_id, thread_type, client, ttl=30000):
    logging.info(f"Đang gửi ảnh đã làm nét đến nhóm {thread_id}")
    # Cập nhật phương thức gửi file:
    try:
        # Upload ảnh lên Imgur
        response = requests.post(
            'https://api.imgur.com/3/upload', 
            headers={'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'},  # Dùng IMGUR_CLIENT_ID của bạn
            files={'image': ('anh_lamnet.jpeg', image_data, 'image/jpeg')}
        )
        imgur_data = response.json()
        if imgur_data['success']:
            img_url = imgur_data['data']['link']
            logging.info(f"Ảnh đã tải lên Imgur: {img_url}")
            client.send(Message(text=img_url), thread_id=thread_id, thread_type=thread_type, ttl=ttl)
        else:
            logging.error(f"Lỗi tải ảnh lên Imgur: {imgur_data}")
            send_error_message(thread_id, thread_type, client, "❌ Lỗi tải ảnh lên dịch vụ lưu trữ.")
    except Exception as e:
        logging.error(f"Lỗi khi tải ảnh lên dịch vụ lưu trữ: {e}")
        send_error_message(thread_id, thread_type, client, "❌ Lỗi tải ảnh lên dịch vụ lưu trữ.")

def send_error_message(thread_id, thread_type, client, error_message="❗ Vui lòng reply hoặc gửi ảnh cần làm nét."):
    logging.error(f"Gửi lỗi cho nhóm {thread_id}: {error_message}")
    client.send(Message(text=error_message), thread_id=thread_id, thread_type=thread_type, ttl=30000)

def get_tmii():
    return {
        'lamnetv2': handle_lamnet_command
    }
