import requests
import json
import os
from zlapi.models import *
from datetime import datetime, timedelta
import pytz
import time

apikey = "8dba54518b401dcea8e3c99afefaad3a"  # OpenWeatherMap API key
vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# Hàm lấy thông tin thời tiết cho một địa điểm
def fetch_weather(area, retries=3):
    try:
        # Lấy thông tin thời tiết từ OpenWeatherMap API
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={requests.utils.quote(area)}&appid={apikey}&units=metric&lang=vi"
        )
        response.raise_for_status()
        data = response.json()
        
        if response.status_code == 200:
            weather = data.get("weather", [{}])[0].get("description", "Không có mô tả")
            temperature = data.get("main", {}).get("temp", "Không có thông tin nhiệt độ")
            humidity = data.get("main", {}).get("humidity", "Không có thông tin độ ẩm")
            feels_like = data.get("main", {}).get("feels_like", "Không có thông tin cảm giác nhiệt độ")
            pressure = data.get("main", {}).get("pressure", "Không có thông tin áp suất")
            wind_speed = data.get("wind", {}).get("speed", "Không có thông tin tốc độ gió")
            wind_deg = data.get("wind", {}).get("deg", "Không có thông tin hướng gió")

            msg = (
                f"📍 **Dự báo thời tiết hôm nay tại {area.title()}**\n"
                f"➡ {weather}\n\n"
                f"🌡 Nhiệt độ: {temperature}°C\n"
                f"🌡 Cảm giác như: {feels_like}°C\n"
                f"💧 Độ ẩm: {humidity}%\n"
                f"🌬 Tốc độ gió: {wind_speed} m/s\n"
                f"🌪 Hướng gió: {wind_deg}°\n"
                f"📏 Áp suất: {pressure} hPa"
            )
            return msg
        else:
            return "❌ Không tìm thấy địa điểm này!"
    except Exception as e:
        if retries > 0:
            time.sleep(1)
            return fetch_weather(area, retries - 1)
        return "❌ Đã có lỗi xảy ra khi lấy dữ liệu thời tiết!"

# Hàm tải danh sách nhóm đã duyệt từ file JSON
def load_duyetbox_data():
    file_path = 'modules/cache/duyetthoitiet37.json'
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

def start_auto(client):
    # Load danh sách nhóm đã duyệt
    allowed_thread_ids = load_duyetbox_data()

    last_sent_time = None
    send_times = ["06:00", "19:00", "20:51"]  # Các mốc giờ gửi thông báo

    # Danh sách các địa điểm muốn lấy thời tiết
    locations = ["Vinh"]

    while True:
        now = datetime.now(vn_tz)
        current_time_str = now.strftime("%H:%M")
        current_second = now.second

        # Kiểm tra đúng thời điểm, tránh gửi lặp
        if current_time_str in send_times and current_second == 0 and current_time_str != last_sent_time:
            for area in locations:  # Lấy thời tiết cho mỗi địa điểm trong danh sách
                weather_info = fetch_weather(area)
                for thread_id in allowed_thread_ids:  # Chỉ gửi vào các nhóm đã duyệt
                    try:
                        client.sendMessage(
                            message=Message(text=f"[ THÔNG BÁO THỜI TIẾT ]\n{weather_info}"),
                            thread_id=thread_id,
                            thread_type=ThreadType.GROUP,
                            ttl=43200000  # Thời gian tồn tại của tin nhắn 12 giờ
                        )
                        print(f"✅ Đã gửi dự báo thời tiết cho nhóm {thread_id} lúc {current_time_str}")
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"❌ Gửi thất bại tới {thread_id}: {e}")
            last_sent_time = current_time_str

        time.sleep(1)  # Kiểm tra mỗi giây để đảm bảo chính xác thời gian
