import json
import os
import requests
import time
import threading
from zlapi.models import Message, ThreadType
from config import ALLOW_GR

# Token người dùng
USER_TOKEN = "XZXHJRJW9PJ1FA3BY6P24WULBX6WUZE6LZ5P"

# Thông tin module
des = {
    'version': "1.2.0",
    'credits': "LAMDev",
    'description': "Module mua hàng taphoammo.net, tự trừ tiền và tự động lấy đơn hàng."
}

# Đường dẫn file số dư
MONEY_PATH = 'modules/oder/money.json'
# Đường dẫn file sản phẩm
APIODER_PATH = 'modules/oder/apioder.json'

# ID Admin
ADMINLAM = '3704058103894860815,776103656827420589'

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_money_entry(zalo_id):
    money_list = load_json(MONEY_PATH)
    for entry in money_list:
        if str(entry.get('id')) == str(zalo_id):
            return
    money_list.append({'id': str(zalo_id), 'sodu': '0'})
    save_json(MONEY_PATH, money_list)

def deduct_money(zalo_id, amount):
    money_list = load_json(MONEY_PATH)
    for entry in money_list:
        if str(entry.get('id')) == str(zalo_id):
            balance = int(entry.get('sodu', 0))
            if balance < amount:
                return False, balance
            entry['sodu'] = str(balance - amount)
            save_json(MONEY_PATH, money_list)
            return True, balance - amount
    return False, 0

def load_apioder():
    return load_json(APIODER_PATH)

def get_product_info(name):
    data = load_apioder()
    for item in data:
        if item.get("name") == name:
            return item
    return None

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and str(sender_id).strip() not in ALLOW_GR:
        return False
    return True

def poll_get_order(client, order_id, message_object, thread_id, thread_type):
    url_get = (
        f"https://taphoammo.net/api/getProducts"
        f"?orderId={order_id}"
        f"&userToken={USER_TOKEN}"
    )
    while True:
        try:
            res_get = requests.get(url_get, timeout=10)
            data_get = res_get.json()
        except:
            time.sleep(10)
            continue

        if data_get.get("success") == "true":
            products = data_get.get("data", [])
            prod_text = "\n".join(f"- {p['product']}" for p in products) if products else "Không có sản phẩm."
            msg = (
                f"✅ ĐÃ LẤY ĐƯỢC ĐƠN HÀNG\n"
                f"Mã đơn hàng: {order_id}\n"
                f"Sản phẩm:\n{prod_text}"
            )
            client.replyMessage(Message(text=msg), message_object, thread_id, thread_type)
            break
        else:
            desc = data_get.get("description", "")
            if desc != "Order in processing!":
                msg = (
                    f"⚠️ Lấy đơn hàng thất bại:\n"
                    f"{desc}\n\n"
                    f"Đơn hàng của bạn: {order_id}"
                )
                client.replyMessage(Message(text=msg), message_object, thread_id, thread_type)
                break
        time.sleep(10)

def handle_muahang(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return

    zalo_id = author_id
    args = message.strip().split()
    if len(args) < 3:
        help_text = (
            "❗ Cú pháp sử dụng:\n"
            "muahang <số_lượng> <tên_sản_phẩm> [mã_giảm_giá]\n\n"
            "Ví dụ:\n"
            "muahang 2 email\n"
            "muahang 1 canvar KM50"
        )
        client.replyMessage(Message(text=help_text), message_object, thread_id, thread_type)
        return

    quantity = int(args[1])
    product_name = args[2]
    promotion = args[3] if len(args) >= 4 else ""

    product_info = get_product_info(product_name)
    if not product_info:
        client.replyMessage(
            Message(text=f"❌ Không tìm thấy sản phẩm '{product_name}' trong apioder.json."),
            message_object, thread_id, thread_type
        )
        return

    price = int(product_info.get("gia", "0"))
    kiosk_token = product_info.get("kioskToken")

    total_cost = price * quantity
    ensure_money_entry(zalo_id)

    success, new_balance = deduct_money(zalo_id, total_cost)
    if not success:
        client.replyMessage(
            Message(text=f"❌ Số dư không đủ. Số dư hiện tại: {new_balance}đ."),
            message_object, thread_id, thread_type
        )
        return

    url_buy = (
        f"https://taphoammo.net/api/buyProducts"
        f"?kioskToken={kiosk_token}"
        f"&userToken={USER_TOKEN}"
        f"&quantity={quantity}"
    )
    if promotion:
        url_buy += f"&promotion={promotion}"

    try:
        res_buy = requests.get(url_buy, timeout=10)
        data_buy = res_buy.json()
    except:
        client.replyMessage(
            Message(text="❌ Lỗi kết nối API mua hàng."),
            message_object, thread_id, thread_type
        )
        return

    if data_buy.get("success") != "true":
        desc = data_buy.get("description", "Không rõ lỗi.")
        client.replyMessage(
            Message(text=f"❌ Mua hàng thất bại: {desc}"),
            message_object, thread_id, thread_type
        )
        return

    order_id = data_buy.get("order_id")

    msg = (
        f"✅ ĐẶT HÀNG THÀNH CÔNG\n"
        f"Mã đơn hàng: {order_id}\n"
        f"Sản phẩm: {product_name}\n"
        f"Giá mỗi SP: {price}đ\n"
        f"Số lượng: {quantity}\n"
        f"Tổng chi phí: {total_cost}đ\n"
        f"Số dư còn lại: {new_balance}đ\n"
        "⏳ Đang chờ lấy sản phẩm, vui lòng đợi..."
    )
    client.replyMessage(Message(text=msg), message_object, thread_id, thread_type)

    t = threading.Thread(target=poll_get_order, args=(client, order_id, message_object, thread_id, thread_type))
    t.start()

def get_tmii():
    return {
        "oder": handle_muahang
    }
