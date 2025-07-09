from zlapi.models import Message
import requests
from config import *

des = {
    'version': "1.0.5",
    'credits': "LAMDev",
    'description': "Chụp màn hình trang web theo yêu cầu"
}

def check_group_access(thread_id, sender_id):
    return True


def handle_cap_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        warning = Message(text="Bạn không có quyền sử dụng lệnh này.")
        client.replyMessage(warning, message_object, thread_id, thread_type, ttl=30000)
        return

    content = message.strip().split()

    if len(content) < 2:
        error_message = Message(text="❌ Vui lòng nhập link cần chụp.")
        client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=30000)
        return

    is_full = False
    url_part = ""

    # /cap full <url>
    if content[1].lower() == "full":
        if len(content) < 3:
            error_message = Message(text="❌ Bạn cần nhập link sau 'full'.")
            client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=30000)
            return
        is_full = True
        url_part = content[2].strip()
    else:
        url_part = content[1].strip()

    # Nếu không có https:// hoặc http:// thì tự thêm
    if not url_part.startswith(("https://", "http://")):
        url_part = "https://" + url_part

    if not validate_url(url_part):
        error_message = Message(text="❌ Vui lòng nhập URL hợp lệ!")
        client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=30000)
        return

    try:
        mode = "full" if is_full else "normal"
        api_url = f"https://api.leanhminh.io.vn/tienich/cap/?url={url_part}&mode={mode}"

        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        api_response = requests.get(api_url, headers=headers)
        api_response.raise_for_status()

        result = api_response.json()

        if result.get("success") and "url" in result:
            image_url = result["url"]

            client.sendImage(
                image_url,
                thread_id=thread_id,
                thread_type=thread_type,
                width=1280,
                height=1280 if not is_full else 2000,
                message = Message(text=f"✅ Đã chụp thành công ({'toàn trang' if is_full else 'mặc định'}):\n{url_part}"),
                ttl=300000
            )

            

        else:
            error_message = Message(text=f"❌ API trả về lỗi: {result.get('message', 'Không rõ lỗi.')}")
            client.sendMessage(error_message, thread_id, thread_type, ttl=30000)

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=30000)

    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type, ttl=30000)

def validate_url(url):
    return url.startswith("https://") or url.startswith("http://")

def get_tmii():
    return {
        'cap2': handle_cap_command
    }
