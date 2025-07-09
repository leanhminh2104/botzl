import os
import requests
from zlapi.models import Message
from config import *  # Giả sử cấu hình của bạn ở đây

# Thông tin mô tả module
des = {
    'version': "1.0.5",
    'credits': "DuongNgocc",
    'description': "Chào bot"
}

# ✅ Kiểm tra quyền truy cập nhóm - mặc định cho phép tất cả
def check_group_access(thread_id, sender_id):
    return True

# ✅ Hàm xử lý khi phát hiện từ khóa chúc ngủ ngon
def hum(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return

    response_text = "[ Bot SIEUTHIMMO - LAMDev ] \nChúc bạn ngủ ngon nhé 💤💤\n:z:z:z:z:z:z"
    # URL âm thanh
    #audio_url = "https://api.leanhminh.x10.mx/chuc-ngu-ngon"
    audio_url = "https://botzl2.leanhminh.io.vn/files/chuc-ngu-ngon.mp3"

    # Gửi tin nhắn văn bản
    client.replyMessage(
        Message(text=response_text),
        message_object,
        thread_id,
        thread_type,
        ttl=600000
    )

    # Gửi sticker
    client.sendSticker(
        stickerType=7,
        stickerId=43552,
        cateId=11788,
        thread_id=thread_id,
        thread_type=thread_type,
        ttl=600000
    )

    # Gửi âm thanh từ URL
    try:
        if audio_url:
            # Kiểm tra URL âm thanh và lấy kích thước file
            head_response = requests.head(audio_url)
            if head_response.status_code == 200:
                file_size = int(head_response.headers.get('content-length', 0))
                client.sendRemoteVoice(
                    voiceUrl=audio_url,
                    thread_id=thread_id,
                    thread_type=thread_type,
                    fileSize=file_size,
                    ttl=500000
                )
            else:
                print(f"❌ URL âm thanh không hợp lệ, mã lỗi: {head_response.status_code}")
                client.replyMessage(
                    Message(text="Không thể gửi âm thanh. Vui lòng kiểm tra lại URL âm thanh."),
                    message_object,
                    thread_id,
                    thread_type,
                    ttl=30000
                )
        else:
            raise ValueError("Không có URL âm thanh.")
    except Exception as e:
        print(f"❌ Lỗi khi gửi âm thanh: {str(e)}")
        client.replyMessage(
            Message(text="Lỗi khi gửi âm thanh. Vui lòng thử lại sau."),
            message_object,
            thread_id,
            thread_type,
            ttl=30000
        )

# ✅ Các từ khóa kích hoạt chức năng
def get_tmii():
    return dict.fromkeys(
        [
            'ngủ', 'ngủ đê', 'im mồm để tau ngủ',
            'zzz', ':z', 'muộn rồi',
            'bye ngủ', 'Ngủ đi', 'ngu day nhe',
            'ngủ bây', 'ngủ nha', 'chúc ngủ ngon',
            't đi ngủ', 'ngủ đây', ':z:z:z', ':z :z :z', 'dm ngủ đê', 'bye', 'bai', 'bai bai'
        ],
        hum
    )
