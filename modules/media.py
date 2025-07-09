import os
import json
import random
import requests
from zlapi import ZaloAPI
from zlapi.models import Message
from config import *

des = {
    'version': "1.0.0",
    'credits': "DuongNgocc",
    'description': "Gửi video, ảnh từ link"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def download_media(link, file_extension):
    try:
        response = requests.get(link, stream=True)
        response.raise_for_status()
        file_path = f"temp_media.{file_extension}"
        with open(file_path, 'wb') as media_file:
            for chunk in response.iter_content(1024):
                media_file.write(chunk)
        return file_path
    except Exception as e:
        print(f"Lỗi khi tải media: {str(e)}")
        return None


def handle_media_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    try:

        link = message.split()[1] if len(message.split()) > 1 else None
        if not link:
            client.send(
                Message(text="Vui lòng cung cấp liên kết media (ảnh hoặc video)."),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return


        if link.endswith(('.jpg', '.jpeg', '.png', '.gif')):

            file_path = download_media(link, "jpg")
            if file_path:
                client.sendLocalImage(file_path, thread_id=thread_id, thread_type=thread_type)
                os.remove(file_path)
            else:
                raise ValueError("Lỗi khi tải ảnh.")
        elif link.endswith(('.mp4', '.mov')):
            client.sendRemoteVideo(
                videoUrl=link,
                thumbnailUrl="https://i.imgur.com/tAmVhh5.mp4", 
                duration=15000, 
                thread_id=thread_id,
                thread_type=thread_type,
                message=Message(text=""),
                width=1080,
                height=1920
            )
        else:
            client.send(
                Message(text="Liên kết không hợp lệ. Chỉ hỗ trợ ảnh (.jpg, .jpeg, .png, .gif) và video (.mp4, .mov)."),
                thread_id=thread_id,
                thread_type=thread_type
            )
    except Exception as e:
        error_message = f"Lỗi xảy ra: {str(e)}"
        client.send(
            Message(text=error_message),
            thread_id=thread_id,
            thread_type=thread_type
        )

def get_tmii():
    return {
        'media': handle_media_command
    }
