import random
import logging
from zlapi.models import Message
from config import ADMIN

des = {
    'version': "1.0.0",
    'credits': "Tai sex",
    'description': "Tạo sticker khi reply vào một ảnh"
}
# Configure logging
logging.basicConfig(level=logging.INFO)

# Danh sách các sticker, thêm 20 sticker cười
laughing_stickers = [
    {"sticker_type": 3, "sticker_id": "10001", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10002", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10003", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10004", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10005", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10006", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10007", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10008", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10009", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10010", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10011", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10012", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10013", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10014", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10015", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10016", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10017", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10018", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10019", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "10020", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "23339", "category_id": "10425"},
]

# Danh sách sticker ban đầu
stickers = [
    {"sticker_type": 3, "sticker_id": "23339", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "12345", "category_id": "10425"},
    {"sticker_type": 3, "sticker_id": "67890", "category_id": "10425"},
]

# Kết hợp cả hai danh sách
all_stickers = stickers + laughing_stickers

def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        client.replyMessage(
            Message(text="Xin lỗi, bạn không có quyền thực hiện hành động này."),
            message_object, thread_id, thread_type
        )
        return

    # Số lượng sticker muốn gửi
    num_stickers_to_send = random.randint(1, 20)

    # Đếm số sticker đã gửi thành công
    success_count = 0

    for _ in range(num_stickers_to_send):
        # Chọn sticker ngẫu nhiên từ danh sách
        selected_sticker = random.choice(all_stickers)
        sticker_type = selected_sticker["sticker_type"]
        sticker_id = selected_sticker["sticker_id"]
        category_id = selected_sticker["category_id"]

        try:
            # Gửi sticker qua client
            response = client.sendSticker(sticker_type, sticker_id, category_id, thread_id, thread_type)

            # Log the response for debugging
            logging.info(f"Response for sticker {sticker_id}: {response}")

            if response and response.get("success"):  # Assuming the API returns a success flag
                logging.info(f"Sticker {sticker_id} sent successfully.")
                success_count += 1
            else:
                logging.warning(f"Failed to send sticker {sticker_id}. Response: {response}")
                client.sendMessage(Message(text="Không thể gửi sticker."), thread_id, thread_type)

        except Exception as e:
            logging.error(f"Error sending sticker {sticker_id}: {e}")
            client.sendMessage(Message(text="Lỗi trong quá trình gửi sticker."), thread_id, thread_type)

    # Gửi tin nhắn thông báo số sticker đã gửi thành công
    client.sendMessage(
        Message(text=f"Đã gửi {success_count}/{num_stickers_to_send} sticker thành công!"),
        thread_id, thread_type
    )

def get_tmii():
    return {
        'spamstk': handle_stk_command
    }