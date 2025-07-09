from zlapi.models import Message
import json
import urllib.parse
import requests
import logging
from config import *
from io import BytesIO

des = {
    'version': "1.5.5",
    'credits': "LAMDev",
    'description': "Làm nét ảnh bằng AI (DeepAI SRGAN), gửi lại ảnh đã làm nét."
}

DEEP_AI_API_KEY = "d453853b-fdf3-482c-b248-73cf71a7f45d"
FAKE_BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/*,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}


def check_group_access(thread_id, sender_id):
    return thread_id in ALLOW_GR or sender_id in ADMIN


def handle_lamnet_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        client.send(Message(text="⛔ Bạn không có quyền dùng lệnh này."), thread_id, thread_type)
        return

    msg = message_object

    # 1) Ảnh gửi trực tiếp
    if msg.msgType == "chat.photo":
        url = urllib.parse.unquote(msg.content.href.replace("\\/", "/"))
        process_and_send_ai(url, thread_id, thread_type, client)
        return

    # 2) Ảnh từ reply
    if msg.quote and msg.quote.attach:
        try:
            data = json.loads(msg.quote.attach)
            url = data.get('hdUrl') or data.get('href')
            if url:
                process_and_send_ai(url, thread_id, thread_type, client)
                return
        except json.JSONDecodeError:
            pass

    client.send(Message(text="❗ Vui lòng gửi hoặc reply một ảnh để làm nét."), 
                thread_id=thread_id, thread_type=thread_type, ttl=30000)


def process_and_send_ai(image_url, thread_id, thread_type, client):
    try:
        # Tải ảnh gốc từ URL
        resp = requests.get(image_url, headers=FAKE_BROWSER_HEADERS, timeout=30)
        resp.raise_for_status()
        file = BytesIO(resp.content)
        file.name = "image.jpg"
    except Exception as e:
        logging.error(f"[lamnet_ai] Lỗi tải ảnh: {e}")
        client.send(Message(text="❌ Không tải được ảnh."), thread_id=thread_id, thread_type=thread_type, ttl=30000)
        return

    # Gửi ảnh tới DeepAI API để làm nét
    try:
        response = requests.post(
            "https://api.deepai.org/api/torch-srgan",  # Hoặc "https://api.deepai.org/api/waifu2x"
            files={'image': file},
            headers={'api-key': DEEP_AI_API_KEY}
        )

        # In ra phản hồi từ API để kiểm tra chi tiết lỗi
        logging.warning(f"[lamnet_ai] DeepAI response status code: {response.status_code}")
        logging.warning(f"[lamnet_ai] DeepAI response content: {response.text}")
        
        if response.status_code != 200:
            raise Exception(f"Lỗi từ API (Mã lỗi {response.status_code}): {response.text}")

        data = response.json()
        
        # Kiểm tra lỗi trong dữ liệu trả về từ API
        if 'output_url' not in data:
            raise Exception("Không nhận được ảnh đã xử lý từ DeepAI.")

        output_url = data.get("output_url")
        if not output_url:
            raise Exception("Không nhận được ảnh đã xử lý từ DeepAI.")

        # Gửi ảnh đã làm nét về lại nhóm
        client.sendImage(
            output_url,
            thread_id=thread_id,
            thread_type=thread_type,
            ttl=300000
        )
        client.send(Message(text="✅ Ảnh đã được AI làm nét và gửi lại."), thread_id=thread_id, thread_type=thread_type)

    except Exception as e:
        logging.error(f"[lamnet_ai] Lỗi xử lý ảnh AI: {e}")
        client.send(Message(text=f"❌ Lỗi xử lý ảnh bằng AI: {e}"), thread_id=thread_id, thread_type=thread_type, ttl=30000)


def get_tmii():
    return {
        'lamnetv3': handle_lamnet_command
    }
