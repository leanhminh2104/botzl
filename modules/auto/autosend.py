import time
import random
import requests
from zlapi.models import Message, ThreadType
from datetime import datetime, timedelta
import pytz
import json
import os

time_messages = {
    "06:00": "Chào Buổi Sáng ! - Bắt Đầu Một Ngày Mới Tràn Đầy Năng Lượng Nào !",
    "06:30": "Lên một đơn tại DICHVUSALE.IO.VN rồi ăn sang thôi nào!",
    "07:00": "Bạn đang có hẹn với DICHVUSALE.IO.VN kìa",
    "10:00": "Làm Việc Và Học Tập Mệt Mỏi - Đừng Quên Nghỉ Ngơi Nhé !",
    "07:00": "Ummmm !!!!! DICHVUSALE.IO.VN\n cũng nghe nhạc đc đó nha :o :o",
    "11:30": "Nghỉ Ngơi Sau Một Buổi Sáng Căng Thẳng Nào :q :q",
    "14:00": "Tới Giờ Làm Việc Tiếp Roi Nè - Chiều Vui Vẻ Nhé !",
    "14:30": "Truy cập ngay wedsite DICHVUSALE.IO.VN thôi nào ",
    "17:00": "Kết Thúc Một Ngày Làm Việc Và Học Tập - Bạn Thấy Thế Nào ?",
    "20:00": "Thư Giãn Sau Ngày Dài Mệt Mỏi Đi Nào !",
    "21:00": "Lên thêm 1 đưn nữa trước khi ngủ nào \nDICHVUSALE.IO.VN",
    "22:21": "Sắp Tới Giờ Ngủ Rồi Nè Hãy Chuẩn Bị Sạc Điện Thoại Nhé !",
    "23:00": "Tới Giờ Ngủ Rồi Chúc Bạn Ngủ Ngon Nhé !\n :z :z :z "
}

vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# Hàm tải dữ liệu nhóm đã duyệt từ tệp JSON
def load_duyetbox_data():
    file_path = 'modules/cache/duyetautosend.json'
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

def start_auto(client):
    try:
        listvd = "https://raw.githubusercontent.com/nguyenductai206/list/refs/heads/main/listvideo.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(listvd, headers=headers)
        response.raise_for_status()
        urls = response.json()
        video_url = random.choice(urls)  # Chọn một video ngẫu nhiên
        thumbnail_url = "https://sv1.anhsieuviet.com/2025/04/16/profile-facebook.png"  # Hình thu nhỏ mặc định
        duration = '20'  # Thời gian video (giây)
    except Exception as e:
        print(f"Error fetching video list: {e}")
        return

    # Tải danh sách nhóm đã duyệt từ duyetboxdata.json
    approved_group_ids = load_duyetbox_data()

    last_sent_time = None

    while True:
        now = datetime.now(vn_tz)
        current_time_str = now.strftime("%H:%M")
        
        if current_time_str in time_messages and (last_sent_time is None or now - last_sent_time >= timedelta(minutes=1)):
            message = time_messages[current_time_str]
            # Gửi thông điệp và video tới các nhóm đã duyệt
            for thread_id in approved_group_ids:
                try:
                    # Gửi video cùng với thông điệp
                    message_to_send = Message(text=f"[ LAMDev - DICHVUSALE\nBây giờ là {current_time_str} ]\n> Auto Send V4: {message}")
                    client.sendRemoteVideo(
                        video_url, 
                        thumbnail_url,
                        duration=duration,
                        message=message_to_send,
                        thread_id=thread_id,
                        thread_type=ThreadType.GROUP,
                        width=1920,  # Kích thước chiều rộng của video
                        height=980,  # Kích thước chiều cao của video
                        ttl=2592000  # Thời gian tồn tại
                    )
                    time.sleep(0.5)  # Giới hạn thời gian giữa các lần gửi
                except Exception as e:
                    print(f"Error sending video to {thread_id}: {e}")
            last_sent_time = now
        
        time.sleep(30)
