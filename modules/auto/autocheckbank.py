import time
import requests
from zlapi.models import Message, ThreadType
from datetime import datetime
import pytz
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==== Cấu hình ====
API_URL = "https://api.dichvusale.io.vn/wed/qrbank/lsgg-mb.php"
QR_IMAGE_URL = "https://img.vietqr.io/image/MB-2104200637-compact.png"
QR_IMAGE_PATH = "modules/cache/temp_qr.jpg"
CACHE_FILE = "modules/cache/last_gd_time.json"
DUYET_FILE = "modules/cache/tbbank.json"
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")


# ==== Đọc nhóm đã duyệt ====
def load_duyet_groups():
    if not os.path.exists(DUYET_FILE):
        return []
    try:
        with open(DUYET_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []


# ==== Ghi lại thời gian giao dịch gần nhất ====
def save_last_time(ts_str):
    with open(CACHE_FILE, "w") as f:
        json.dump({"last": ts_str}, f)


# ==== Đọc thời gian giao dịch gần nhất đã gửi ====
def load_last_time():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            return data.get("last")
    except:
        return None


# ==== So sánh thời gian kiểu dd/mm/yyyy HH:MM:SS ====
def is_newer(ts1, ts2):
    try:
        dt1 = datetime.strptime(ts1, "%d/%m/%Y %H:%M:%S")
        dt2 = datetime.strptime(ts2, "%d/%m/%Y %H:%M:%S")
        return dt1 > dt2
    except:
        return True


# ==== Hàm chính khởi chạy auto ====
def start_auto(client):
    last_ts = load_last_time()
    approved_groups = load_duyet_groups()

    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    while True:
        try:
            response = session.get(API_URL, timeout=20)
            data = response.json()

            if not data.get("success"):
                print("⚠️ API không phản hồi thành công.")
                time.sleep(60)
                continue

            ds = sorted(
                [x for x in data.get("data", []) if x.get("loai") == "Giao dịch đến"],
                key=lambda d: datetime.strptime(d["timestamp"], "%d/%m/%Y %H:%M:%S"),
                reverse=True
            )

            if not ds:
                print("⚠️ Không có giao dịch đến.")
                time.sleep(60)
                continue

            gd = ds[0]
            current_ts = gd.get("timestamp")
            if not last_ts or is_newer(current_ts, last_ts):
                print(f"🚀 Phát hiện GD mới: {current_ts}")
                msg = f"""📥 GIAO DỊCH ĐẾN MỚI

🧾 Thời gian: {gd.get("timestamp", "-")}
💰 Số tiền: {int(gd.get("sotien", "0")):,} đ
📄 Nội dung: {gd.get("noidung", "-")}
📌 Trạng thái: {gd.get("trangthai", "-")}

👉 BOT AUTO BANK DICHVUSALE"""

                # Tải ảnh QR
                image_downloaded = False
                try:
                    img = session.get(QR_IMAGE_URL, timeout=10)
                    with open(QR_IMAGE_PATH, "wb") as f:
                        f.write(img.content)
                    image_downloaded = True
                    print("✅ Ảnh QR đã tải.")
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ Không tải được ảnh QR: {e}")

                # Gửi vào nhóm
                print("✅ Danh sách nhóm đã duyệt:", approved_groups)
                for group_id in approved_groups:
                    print(f"📤 Đang gửi tới nhóm {group_id}...")
                    try:
                        if image_downloaded and os.path.exists(QR_IMAGE_PATH):
                            print("📸 Đang gửi ảnh...")
                            client.sendLocalImage(
                                QR_IMAGE_PATH,
                                thread_id=group_id,
                                thread_type=ThreadType.GROUP,
                                width=500,
                                height=500,
                                message=Message(text=msg.strip()),
                                ttl=6000000
                            )
                            print("✅ Đã gửi ảnh QR.")
                        else:
                            print("💬 Đang gửi tin nhắn...")
                            client.sendMessage(
                                Message(text=msg.strip()),
                                thread_id=group_id,
                                thread_type=ThreadType.GROUP,
                               ttl=6000000
                            )
                            print("✅ Đã gửi tin nhắn.")
                        time.sleep(1)
                    except Exception as e:
                        print(f"❌ Lỗi gửi nhóm {group_id}: {e}")

                save_last_time(current_ts)
                last_ts = current_ts
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi kết nối API: {e}")
        except Exception as e:
            print(f"❌ Lỗi xử lý giao dịch: {e}")

        time.sleep(30)
