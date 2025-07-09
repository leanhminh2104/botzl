import os
import requests
from datetime import datetime
from zlapi.models import Message
from zlapi import ZaloAPIException
from config import *

des = {
    'version': "1.3.0",
    'credits': "LAMDev",
    'description': "Hiển thị thông tin nhóm đầy đủ (tên, ID, mô tả, số thành viên, ảnh đại diện, mã hóa...)"
}

def check_group_access(thread_id, sender_id):
    return not (thread_id in ALLOW_GR)

def handle_group_info_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return

    try:
        print(f"📥 Đang lấy thông tin nhóm cho thread_id: {thread_id}")
        group_data = client.fetchGroupInfo(thread_id)

        if not group_data or not hasattr(group_data, "gridInfoMap"):
            raise ValueError("Không lấy được thông tin nhóm.")

        info = group_data.gridInfoMap.get(str(thread_id))
        if not info:
            raise ValueError("Không tìm thấy thông tin nhóm trong gridInfoMap.")

        # Các trường thông tin chính
        group_id = info.get("groupId", str(thread_id))
        group_name = info.get("name", "Không rõ")
        group_desc = info.get("desc", "Không có mô tả")
        creator_id = info.get("creatorId", "Không rõ")
        created_time = int(info.get("createdTime", 0)) // 1000
        created_at = datetime.fromtimestamp(created_time).strftime('%H:%M %d/%m/%Y') if created_time else "Không rõ"

        member_count = info.get("totalMember", "Không rõ")
        max_member = info.get("maxMember", "Không rõ")
        is_e2ee = info.get("e2ee", 0)
        is_private = "Riêng tư" if info.get("visibility", 0) == 1 else "Công khai"
        subtype = info.get("subType", 0)
        group_type = "Nhóm thường" if subtype == 1 else "Nhóm con" if subtype == 2 else "Không rõ"

        global_id = info.get("globalId", "Không rõ")
        group_avatar = info.get("fullAvt") or info.get("avt")

        # Tạo thông điệp
        msg_text = (
            f"📌 **THÔNG TIN NHÓM ZALO**\n"
            f"👥 Tên nhóm: {group_name}\n"
            f"🆔 ID nhóm: {group_id}\n"
            f"🔗 Global ID: {global_id}\n"
            f"🔒 Quyền riêng tư: {is_private} | Mã hóa: {'Bật' if is_e2ee else 'Tắt'}\n"
            f"🧾 Loại nhóm: {group_type}\n"
            f"👤 ID người tạo: {creator_id}\n"
            f"📅 Ngày tạo: {created_at}\n"
            f"👨‍👩‍👧‍👦 Số thành viên: {member_count}/{max_member}\n"
            f"📄 Mô tả: {group_desc or 'Không có mô tả'}"
        )

        message_to_send = Message(text=msg_text)

        # Gửi kèm ảnh đại diện nếu có
        if group_avatar:
            try:
                response = requests.get(group_avatar, timeout=10)
                if response.ok:
                    image_path = "temp_group_avatar.jpg"
                    with open(image_path, 'wb') as f:
                        f.write(response.content)

                    client.sendLocalImage(
                        image_path,
                        message=message_to_send,
                        thread_id=thread_id,
                        thread_type=thread_type,
                        ttl=300000
                    )
                    os.remove(image_path)
                else:
                    raise Exception("Không thể tải ảnh nhóm (mã lỗi ảnh).")
            except Exception as e:
                print(f"⚠️ Lỗi khi gửi ảnh: {e}")
                client.sendMessage(Message(text=msg_text + "\n⚠️ Không thể tải ảnh đại diện."), thread_id, thread_type, ttl=3000)
        else:
            client.sendMessage(message_to_send, thread_id, thread_type, ttl=300000)

    except ZaloAPIException as zae:
        print(f"❌ ZaloAPI lỗi: {zae}")
        client.sendMessage(Message(text=f"❌ Lỗi ZaloAPI: {str(zae)}"), thread_id, thread_type, ttl=3000)

    except Exception as e:
        print(f"❌ Lỗi xử lý: {e}")
        client.sendMessage(Message(text=f"❌ Lỗi: {str(e)}"), thread_id, thread_type, ttl=3000)

def get_tmii():
    return {
        'in4gr': handle_group_info_command
    }
