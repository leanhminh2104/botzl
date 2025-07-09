import json
import os
import time
from zlapi.models import Message, ThreadType
from config import ALLOW_GR  # Đảm bảo bạn có biến này trong config
# Gán các ID admin, cách nhau bằng dấu phẩy
ADMINLAM = '3704058103894860815,776103656827420589'

# Thông tin module
des = {
    'version': "1.0.6",
    'credits': "LAMDev",
    'description': (
        "Duyệt nhóm, ban nhóm, duyệt tất cả, ban tất cả, duyệt theo ID, ban theo ID, "
        "xem danh sách nhóm đã duyệt và chưa duyệt"
    )
}

# Kiểm tra quyền admin
def is_admin(author_id):
    admin_ids = [x.strip() for x in ADMINLAM.split(',')]
    return str(author_id).strip() in admin_ids

# Tải dữ liệu duyệt nhóm
def load_duyetbox_data():
    path = 'modules/cache/duyetthoitiet37.json'
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

# Lưu dữ liệu duyệt nhóm
def save_duyetbox_data(data):
    with open('modules/cache/duyetthoitiet37.json', 'w') as f:
        json.dump(data, f, indent=4)

# Kiểm tra xem user có được thao tác với nhóm không
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and str(sender_id).strip() not in ALLOW_GR:
        return False
    return True

# Xử lý lệnh thoitiet37
def handle_duyetbox_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return

    if not is_admin(author_id):
        client.replyMessage(
            Message(text="• Bạn không đủ quyền để sử dụng lệnh này."),
            message_object, thread_id, thread_type, ttl=30000
        )
        return

    text = message.split()
    if len(text) < 2:
        help_text = (
            "• Vui lòng nhập đúng cú pháp lệnh:\n"
            "→ thoitiet37 duyet\n"
            "→ thoitiet37 ban\n"
            "→ thoitiet37 duyetid <id>\n"
            "→ thoitiet37 banid <id>\n"
            "→ thoitiet37 duyetall\n"
            "→ thoitiet37 banall\n"
            "→ thoitiet37 listduyet\n"
            "→ thoitiet37 list-approved"
        )
        client.replyMessage(Message(text=help_text), message_object, thread_id, thread_type, ttl=30000)
        return

    action = text[1].lower()
    data = load_duyetbox_data()
    current_time = time.strftime("%H:%M:%S - %d/%m/%Y", time.localtime())
    group_info = client.fetchGroupInfo(thread_id)
    group_name = group_info.gridInfoMap.get(thread_id, {}).get('name', 'Không rõ')

    if action == "duyet":
        if thread_id not in data:
            data.append(thread_id)
            save_duyetbox_data(data)
            msg = f"• Đã duyệt nhóm\n• Tên: {group_name}\n• ID: {thread_id}\n• Lúc: {current_time}"
        else:
            msg = "• Nhóm đã được duyệt trước đó."

    elif action == "duyetid" and len(text) > 2:
        target_id = text[2]
        if target_id not in data:
            data.append(target_id)
            save_duyetbox_data(data)
            name = client.fetchGroupInfo(target_id).gridInfoMap.get(target_id, {}).get('name', 'Không rõ')
            msg = f"• Đã duyệt nhóm\n• Tên: {name}\n• ID: {target_id}\n• Lúc: {current_time}"
            client.sendMessage(Message(text="• Nhóm của bạn đã được duyệt bởi ADMIN"), target_id, ThreadType.GROUP, ttl=30000)
        else:
            msg = "• Nhóm này đã được duyệt."

    elif action == "ban":
        if thread_id in data:
            data.remove(thread_id)
            save_duyetbox_data(data)
            msg = f"• Đã ban nhóm\n• Tên: {group_name}\n• ID: {thread_id}\n• Lúc: {current_time}"
        else:
            msg = "• Nhóm chưa được duyệt, không thể ban."

    elif action == "banid" and len(text) > 2:
        target_id = text[2]
        if target_id in data:
            data.remove(target_id)
            save_duyetbox_data(data)
            name = client.fetchGroupInfo(target_id).gridInfoMap.get(target_id, {}).get('name', 'Không rõ')
            msg = f"• Đã ban nhóm\n• Tên: {name}\n• ID: {target_id}\n• Lúc: {current_time}"
            client.sendMessage(Message(text="• Nhóm của bạn đã bị ban"), target_id, ThreadType.GROUP, ttl=30000)
        else:
            msg = "• Nhóm chưa được duyệt, không thể ban."

    elif action == "duyetall":
        all_ids = list(client.fetchAllGroups().gridVerMap.keys())
        new = [i for i in all_ids if i not in data]
        data.extend(new)
        save_duyetbox_data(data)
        msg = "> Đã duyệt toàn bộ nhóm:\n" + "\n".join(
            f"{i+1}. {client.fetchGroupInfo(g).gridInfoMap.get(g, {}).get('name', 'Không rõ')} ({g})"
            for i, g in enumerate(new)
        ) if new else "• Tất cả nhóm đã được duyệt."

    elif action == "banall":
        banned = data.copy()
        data.clear()
        save_duyetbox_data(data)
        msg = "> Đã ban toàn bộ nhóm:\n" + "\n".join(
            f"{i+1}. {client.fetchGroupInfo(g).gridInfoMap.get(g, {}).get('name', 'Không rõ')} ({g})"
            for i, g in enumerate(banned)
        ) if banned else "• Không có nhóm nào để ban."

    elif action == "listduyet":
        msg = "> Danh sách nhóm đã duyệt:\n" + "\n".join(
            f"{i+1}. {client.fetchGroupInfo(g).gridInfoMap.get(g, {}).get('name', 'Không rõ')} ({g})"
            for i, g in enumerate(data)
        ) if data else "• Không có nhóm nào được duyệt."

    elif action == "list-approved":
        all_ids = list(client.fetchAllGroups().gridVerMap.keys())
        not_approved = [i for i in all_ids if i not in data]
        msg = "> Danh sách nhóm chưa duyệt:\n" + "\n".join(
            f"{i+1}. {client.fetchGroupInfo(g).gridInfoMap.get(g, {}).get('name', 'Không rõ')} ({g})"
            for i, g in enumerate(not_approved)
        ) if not_approved else "• Tất cả nhóm đã được duyệt."

    else:
        msg = (
            "• Vui lòng nhập đúng cú pháp lệnh:\n"
            "→ thoitiet37 duyet\n"
            "→ thoitiet37 ban\n"
            "→ thoitiet37 duyetid <id>\n"
            "→ thoitiet37 banid <id>\n"
            "→ thoitiet37 duyetall\n"
            "→ thoitiet37 banall\n"
            "→ thoitiet37 listduyet\n"
            "→ thoitiet37 list-approved"
        )

    client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=30000)

# Đăng ký hàm cho bot
def get_tmii():
    return {
        'thoitiet37': handle_duyetbox_command
    }
