import os
from zlapi.models import Message
import requests
from config import *

des = {
    'version': "1.0.5",
    'credits': "DuongNgocc",
    'description': "Chào bot"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def hum(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    
    response_text = ""
    
    
    audio_url = "https://botzl2.leanhminh.io.vn/files/chuc-ngu-ngon.mp3"
    
    
    client.replyMessage(
        Message(
            text=response_text
        ),
        message_object,
        thread_id,
        thread_type,
        ttl=30000
    )

    
    client.sendSticker(
        stickerType=7,
        stickerId=29557,  
        cateId=10882,     
        thread_id=thread_id,
        thread_type=thread_type,
        ttl=600000
    )

    try:
        if audio_url:
            print(f"Đang gửi âm thanh từ URL: {audio_url}")
            
            client.sendRemoteVoice(
                voiceUrl=audio_url,  
                thread_id=thread_id,
                thread_type=thread_type,
                ttl=600000
            )
            print("Âm thanh đã được gửi thành công.")
        else:
            print(f"Không tìm thấy URL âm thanh.")
            client.replyMessage(
                Message(
                    text="Không thể gửi âm thanh. Vui lòng kiểm tra lại URL âm thanh."
                ),
                message_object,
                thread_id,
                thread_type,
                ttl=10000
            )
    except Exception as e:
        print(f"Lỗi khi gửi âm thanh: {str(e)}")
        client.replyMessage(
            Message(
                text="Lỗi khi gửi âm thanh. Vui lòng thử lại sau."
            ),
            message_object,
            thread_id,
            thread_type,
            ttl=10000
        )

def get_tmii():
    
    return dict.fromkeys(
        ['hunhun', 'humhum'],  
        hum
    )