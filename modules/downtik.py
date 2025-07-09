from zlapi.models import Message
import requests
from config import *

des = {
    'version': "1.0.2",
    'credits': "DuongNgocc",
    'description': "𝕋𝕒̉𝕚 𝕧𝕚𝕕𝕖𝕠 𝕥𝕚𝕜𝕥𝕠𝕜"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_tiktok_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    content = message.strip().split()

    if len(content) < 2:
        error_message = Message(text="Vui lòng nhập một đường link TikTok hợp lệ.")
        client.replyMessage(error_message, message_object, thread_id, thread_type,ttl=60000)
        return

    video_link = content[1].strip()

    if not video_link.startswith("https://"):
        error_message = Message(text="Vui lòng nhập một đường link TikTok hợp lệ (bắt đầu bằng https://).")
        client.replyMessage(error_message, message_object, thread_id, thread_type,ttl=60000)
        return

    api_url = f'https://api.sumiproject.net/tiktok?video={video_link}'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_8_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.6 Mobile/15E148 Safari/604.1'
        }

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        if 'data' not in data or 'play' not in data['data']:
            error_message = Message(text=f"Không thể lấy được link video từ API cho {video_link}.")
            client.sendMessage(error_message, thread_id, thread_type,ttl=60000)
            return

        videoUrl = data['data']['play']
        titlevd = data['data']['title']
        sendtitle = f"Caption:\n {titlevd}"

        messagesend = Message(text=sendtitle)

        thumbnailUrl = 'https://files.catbox.moe/gjg8fg.jpeg'
        duration = '1000'

        client.sendRemoteVideo(
            videoUrl, 
            thumbnailUrl,
            duration=duration,
            message=messagesend,
            thread_id=thread_id,
            thread_type=thread_type,ttl=60000,
            width=1200,
            height=1600
        )

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type,ttl=60000)
    except KeyError as e:
        error_message = Message(text=f"Dữ liệu từ API không đúng cấu trúc: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type,ttl=60000)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type,ttl=60000)

def get_tmii():
    return {
        'downtik': handle_tiktok_command
    }
