from zlapi.models import Message
import requests
from config import *

des = {
    'version': "1.0.4",
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
        error_message = Message(text="Vui lòng nhập link cần chụp.")
        client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=30000)
        return

    input_url = content[1].strip()

    # Nếu không có https:// hoặc http:// thì tự thêm
    if not input_url.startswith(("https://", "http://")):
        input_url = "https://" + input_url

    if not validate_url(input_url):
        error_message = Message(text="Vui lòng nhập URL hợp lệ!")
        client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=30000)
        return

    try:
        api_url = f"https://api.leanhminh.io.vn/tienich/cap/?url={input_url}"
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
                height=1280,
                message = Message(text=f"✅ Đã chụp thành công:\n{input_url}"),
                ttl=500000
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
        'cap': handle_cap_command
    }
