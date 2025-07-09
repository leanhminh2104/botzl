from zlapi.models import Message
import requests
import random
from config import *

des = {
    'version': "2.2.0",
    'credits': "LAMDev",
    'description': "Chat với Gemini trực tiếp qua nhiều API key"
}

# Danh sách API key Gemini của bạn
GEMINI_API_KEYS = [
    ###"AIzaSyCIRsntET8L0hnXX6hNA2HQvp8Z81Yz2qM",
    ###"AIzaSyC7SBAwwbJfgsGp6mca6OsZgBD0A8KWOFk",
    ###"AIzaSyBzhPkDjYttBP5YhQHmIYMx0emQu0Z4UMk",
    "AIzaSyDdEFiGxzmdIzOHI_rbDdg-WV8feUxVFVQ"
]

# Kiểm tra quyền truy cập nhóm
def check_group_access(thread_id, sender_id):
    return thread_id not in ALLOW_GR

# Xử lý lệnh GEMINI
def handle_gemini_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return

    text = message.strip().split()

    if len(text) < 2:
        client.sendMessage(
            Message(text="❗ Vui lòng nhập câu hỏi để trò chuyện cùng Gemini."),
            thread_id, thread_type, ttl=30000
        )
        return

    user_question = " ".join(text[1:])

    # Tạo nội dung gửi đi
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": user_question
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Thử lần lượt các API key
    for api_key in random.sample(GEMINI_API_KEYS, len(GEMINI_API_KEYS)):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()

            # Nếu có phản hồi hợp lệ
            if 'candidates' in data:
                parts = data['candidates'][0].get('content', {}).get('parts', [])
                if parts and 'text' in parts[0]:
                    gpt_response = parts[0]['text']
                else:
                    gpt_response = "⚠️ Không tìm thấy phản hồi từ Gemini."
                client.sendMessage(Message(text=gpt_response), thread_id, thread_type, ttl=300000)
                return

            # Nếu có lỗi
            elif 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                print(f"[Gemini] Key lỗi: {api_key} - {error_msg}")
                continue  # Thử key tiếp theo

        except Exception as e:
            print(f"[Gemini] Exception: {api_key} - {str(e)}")
            continue  # Thử key tiếp theo

    # Nếu không có key nào thành công
    client.sendMessage(
        Message(text="❌ Tất cả API key đều đang bị lỗi hoặc quá giới hạn. Vui lòng thử lại sau."),
        thread_id, thread_type, ttl=30000
    )

# Trả về dict command cho bot
def get_tmii():
    return {
        'gemini': handle_gemini_command
    }
