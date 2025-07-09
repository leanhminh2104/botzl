from zlapi.models import Message
import requests
import os
from config import *

des = {
    'version': "1.0.2",
    'credits': "DuongNgocc",
    'description': "Lấy thông tin facebook từ link facebook"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_fbinfo_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    content = message.strip().split()

    if len(content) < 2:
        error_message = Message(text="Vui lòng nhập một đường link Facebook hợp lệ.")
        client.replyMessage(error_message, message_object, thread_id, thread_type)
        return

    linkfb = content[1].strip()

    if not linkfb.startswith("https://"):
        error_message = Message(text="Vui lòng nhập link Facebook hợp lệ!")
        client.replyMessage(error_message, message_object, thread_id, thread_type)
        return

    apiuid = f'https://ffb.vn/api/tool/get-id-fb?idfb={linkfb}'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        response = requests.get(apiuid, headers=headers)
        response.raise_for_status()

        data = response.json()
        uidfb = data.get('id')

        if not uidfb:
            error_message = Message(text="Không tìm thấy UID từ link Facebook đã cung cấp.")
            client.replyMessage(error_message, message_object, thread_id, thread_type)
            return

        getinfo = f'https://freeapi.mxhgiare.net/facebook/info?uid={uidfb}'
        response = requests.get(getinfo, headers=headers)
        response.raise_for_status()

        data = response.json()

        ten = data.get('name', 'Không có thông tin')
        linkacc = data.get('link_profile', 'Không có thông tin')
        uidacc = data.get('uid', 'Không có thông tin')
        usernsmeacc = data.get('username', 'Không có thông tin')
        tgtaoscc = data.get('created_time', 'Không có thông tin')
        website = data.get('web', 'Không có thông tin')
        trangthai = data.get('relationship_status', 'Không có thông tin')
        ntns = data.get('birthday', 'Không có thông tin')
        fl = data.get('follower', 'Không có thông tin')
        tx = data.get('tichxanh', 'Không có thông tin')
        diachi = data.get('location', 'Không có thông tin')
        avt = data.get('avatar', '')

        guimess = (
            f"• Tên Facebook: {ten}\n"
            f"• Link Facebook: {linkacc}\n"
            f"• UID Facebook: {uidacc}\n"
            f"• Username Facebook: {usernsmeacc}\n"
            f"• Thời gian tạo tài khoản: {tgtaoscc}\n"
            f"• Website: {website}\n"
            f"• Trạng thái: {trangthai}\n"
            f"• Sinh nhật: {ntns}\n"
            f"• Follower: {fl}\n"
            f"• Tích xanh: {tx}\n"
            f"• Địa chỉ: {diachi}"
        )
        sendtn = Message(text=guimess)

        if avt:
            image_response = requests.get(avt, headers=headers)
            image_path = 'modules/cache/temp_image3.jpeg'

            with open(image_path, 'wb') as f:
                f.write(image_response.content)

            client.sendLocalImage(
                image_path, 
                message=sendtn,
                thread_id=thread_id,
                thread_type=thread_type,
                width=2500,
                height=2500
            )

            os.remove(image_path)
        else:
            client.sendMessage(sendtn, thread_id, thread_type)

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def get_tmii():
    return {
        'infofb': handle_fbinfo_command
    }
