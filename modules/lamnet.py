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
    'version': "1.5.4",
    'credits': "LAMDev",
    'description': "Làm nét ảnh, upload Imgur và gửi ảnh qua URL (link trực tiếp)"
}

last_sent_image_url = None

FAKE_BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/*,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

IMGUR_CLIENT_ID = 'f5494b2d26f43c2'


def check_group_access(thread_id, sender_id):
    return thread_id in ALLOW_GR or sender_id in ADMIN


def handle_lamnet_command(message, message_object, thread_id, thread_type, author_id, client):
    global last_sent_image_url
    if not check_group_access(thread_id, author_id):
        client.send(Message(text="⛔ Bạn không có quyền dùng lệnh này."), thread_id, thread_type)
        return

    msg = message_object

    # 1) Ảnh gửi trực tiếp
    if msg.msgType == "chat.photo":
        url = urllib.parse.unquote(msg.content.href.replace("\\/", "/"))
        last_sent_image_url = url
        process_and_send(url, thread_id, thread_type, client)
        return

    # 2) Ảnh từ reply
    if msg.quote and msg.quote.attach:
        try:
            data = json.loads(msg.quote.attach)
            url = data.get('hdUrl') or data.get('href')
            if url:
                last_sent_image_url = url
                process_and_send(url, thread_id, thread_type, client)
                return
        except json.JSONDecodeError:
            pass

    client.send(Message(text="❗ Vui lòng gửi hoặc reply một ảnh để làm nét."), 
                thread_id=thread_id, thread_type=thread_type, ttl=30000)


def process_and_send(image_url, thread_id, thread_type, client):
    try:
        # Tải ảnh gốc
        resp = requests.get(image_url, headers=FAKE_BROWSER_HEADERS, timeout=30)
        resp.raise_for_status()
        pil = Image.open(io.BytesIO(resp.content)).convert("RGB")
        arr = np.array(pil)
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    except Exception as e:
        logging.error(f"Tải/mở ảnh lỗi: {e}")
        client.send(Message(text="❌ Không tải được ảnh."), thread_id=thread_id, thread_type=thread_type, ttl=30000)
        return

    # Làm nét ảnh
    try:
        sharp = bgr.copy()
        lab = cv2.cvtColor(sharp, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        sharp = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        _, enc = cv2.imencode('.jpg', sharp, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        data = enc.tobytes()
    except Exception as e:
        logging.error(f"Lỗi khi xử lý ảnh: {e}")
        client.send(Message(text="❌ Lỗi xử lý ảnh."), thread_id=thread_id, thread_type=thread_type, ttl=30000)
        return


    # Upload lên Imgur
    imgur_url = upload_image_to_imgur(data)
    if not imgur_url:
        logging.error("Lỗi tải ảnh lên Imgur")
        client.send(Message(text="❌ Không gửi được ảnh (upload thất bại)."), thread_id, thread_type, ttl=30000)
        return

    # Gửi bằng link ảnh
    try:
        client.sendImage(
            imgur_url,
            thread_id=thread_id,
            thread_type=thread_type,
            ttl=300000
        )
        client.send(Message(text="✅ Ảnh đã được làm nét và gửi lại."), thread_id, thread_type)
    except Exception as e:
        logging.error(f"Lỗi gửi ảnh qua link: {e}")
        client.send(Message(text="❌ Lỗi gửi ảnh qua link."), thread_id, thread_type, ttl=30000)


def upload_image_to_imgur(image_data):
    try:
        files = {'image': ('lamnet.jpg', image_data, 'image/jpeg')}
        response = requests.post(
            'https://api.imgur.com/3/image',
            headers={'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'},
            files=files
        )
        data = response.json()
        if data.get('success'):
            return data['data']['link']
    except Exception as e:
        logging.error(f"Lỗi khi upload Imgur: {e}")
    return None


def get_tmii():
    return {
        'lamnet': handle_lamnet_command
    }
