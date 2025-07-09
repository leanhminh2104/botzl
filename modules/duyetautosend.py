import json
from zlapi.models import *
from config import *
import os
import time

des = {
    'version': "1.0.6",
    'credits': "LAMDev",
    'description': "Duyệt nhóm, ban nhóm, ban all nhóm, duyệt all nhóm, duyệt nhóm theo id, ban nhóm theo id, xem toàn bộ nhóm chưa duyệt, xem toàn bộ nhóm đã duyệt"
}

# ADMINLAM chứa nhiều ID, cách nhau bằng dấu phẩy
ADMINLAM = '3704058103894860815, 776103656827420589'

# Hàm kiểm tra quyền admin: chuyển cả author_id và các admin trong ADMINLAM về kiểu string sau khi loại bỏ khoảng trắng
def is_admin(author_id):
    admin_ids = [admin_id.strip() for admin_id in ADMINLAM.split(',')]
    return str(author_id).strip() in admin_ids

def load_duyetbox_data():
    file_path = 'modules/cache/duyetautosend.json'
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

def save_duyetbox_data(data):
    with open('modules/cache/duyetautosend.json', 'w') as f:
        json.dump(data, f, indent=4)

def check_group_access(thread_id, sender_id):
    # Nếu thread_id thuộc nhóm cho phép và sender_id không phải admin, không cho phép
    if thread_id in ALLOW_GR and str(sender_id).strip() not in ALLOW_GR:
        return False
    return True  
    # Lệnh print này sẽ không bao giờ được thực thi vì nó nằm sau return

def handle_duyetbox_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    group_info = client.fetchGroupInfo(thread_id)
    group_name = group_info.gridInfoMap.get(thread_id, {}).get('name', 'None')
    current_time = time.strftime("%H:%M:%S - %d/%m/%Y", time.localtime())

    if not is_admin(author_id):
        response_message = "• Bạn không đủ quyền hạn để sử dụng lệnh này."
        client.replyMessage(Message(text=response_message), message_object, thread_id, thread_type, ttl=30000)
        return

    text = message.split()
    if len(text) < 2:
        error_message = ("Vui lòng nhập lệnh đầy đủ: \n"
                         "`autosend duyet`,\n"
                         "`autosend ban`,\n"
                         "`autosend duyetall`,\n"
                         "`autosend banall`,\n"
                         "`autosend listduyet`,\n"
                         "`autosend list-approved`,\n"
                         "`autosend banid`,\n"
                         "`autosend duyetid`")
        client.sendMessage(Message(text=error_message), thread_id, thread_type, ttl=30000)
        return

    action = text[1].lower()
    data = load_duyetbox_data()
    
    if action == "duyet":
        if thread_id not in data:
            data.append(thread_id)
            save_duyetbox_data(data)
            success_message = (f"• Đã duyệt nhóm thành công\n"
                               f"• Nhóm: {group_name}\n"
                               f"• ID nhóm: {thread_id}\n"
                               f"• Vào lúc: {current_time}.")
        else:
            success_message = "• Nhóm này đã được duyệt trước đó."

    elif action == "duyetid" and len(text) > 2:
        target_group_id = text[2]
        if target_group_id not in data:
            data.append(target_group_id)
            save_duyetbox_data(data)
            target_group_name = client.fetchGroupInfo(target_group_id).gridInfoMap.get(target_group_id, {}).get('name', 'None')
            success_message = (f"• Đã duyệt nhóm với ID {target_group_id} thành công\n"
                               f"• Nhóm: {target_group_name}\n"
                               f"• Vào lúc: {current_time}.")
            gui = Message(text="Nhóm của bạn đã được ADMIN duyệt chức năng Autosend")
            client.sendMessage(gui, thread_id=target_group_id, thread_type=ThreadType.GROUP, ttl=30000)
        else:
            success_message = f"• Nhóm với ID {target_group_id} đã được duyệt trước đó."
    
    elif action == "ban":
        if thread_id in data:
            data.remove(thread_id)
            save_duyetbox_data(data)
            success_message = (f"• Ban nhóm thành công khỏi danh sách duyệt\n"
                               f"• Nhóm: {group_name}\n"
                               f"• ID nhóm: {thread_id}\n"
                               f"• Vào lúc: {current_time}.")
        else:
            success_message = "• Nhóm này chưa được duyệt, không thể ban."

    elif action == "banid" and len(text) > 2:
        target_group_id = text[2]
        if target_group_id in data:
            data.remove(target_group_id)
            save_duyetbox_data(data)
            target_group_name = client.fetchGroupInfo(target_group_id).gridInfoMap.get(target_group_id, {}).get('name', 'None')
            success_message = (f"• Đã ban nhóm với ID {target_group_id} thành công\n"
                               f"• Nhóm: {target_group_name}\n"
                               f"• Vào lúc: {current_time}.")
            gui = Message(text="Nhóm của bạn đã bị ban, không thể sử dụng")
            client.sendMessage(gui, thread_id=target_group_id, thread_type=ThreadType.GROUP, ttl=30000)
        else:
            success_message = f"• Nhóm với ID {target_group_id} chưa được duyệt, không thể ban."

    elif action == "duyetall":
        all_group_ids = list(client.fetchAllGroups().gridVerMap.keys())
        newly_approved_groups = [group_id for group_id in all_group_ids if group_id not in data]
        data.extend(newly_approved_groups)
        save_duyetbox_data(data)
        group_list = "> Đã duyệt thành công toàn bộ nhóm:\n" + "\n".join(
            f"{i+1}:\n• Tên nhóm: {client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {}).get('name', 'None')}\n• ID: {group_id}"
            for i, group_id in enumerate(newly_approved_groups)
        )
        success_message = group_list if newly_approved_groups else "Tất cả các nhóm đã được duyệt."

    elif action == "banall":
        banned_groups = [group_id for group_id in data]
        data.clear()
        save_duyetbox_data(data)
        group_list = "> Đã ban thành công toàn bộ nhóm:\n" + "\n".join(
            f"{i+1}:\n• Tên nhóm: {client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {}).get('name', 'None')}\n• ID: {group_id}"
            for i, group_id in enumerate(banned_groups)
        )
        success_message = group_list if banned_groups else "Không có nhóm nào trong danh sách duyệt để ban."

    elif action == "listduyet":
        approved_groups = [group_id for group_id in data]
        group_list = "> Danh sách nhóm đã duyệt:\n" + "\n".join(
            f"{i+1}:\n• Tên nhóm: {client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {}).get('name', 'None')}\n• ID: {group_id}"
            for i, group_id in enumerate(approved_groups)
        )
        success_message = group_list if approved_groups else "Không có nhóm nào được duyệt."

    elif action == "list-approved":
        all_group_ids = list(client.fetchAllGroups().gridVerMap.keys())
        unapproved_groups = [group_id for group_id in all_group_ids if group_id not in data]
        group_list = "> Các nhóm chưa được duyệt:\n" + "\n".join(
            f"{i+1}:\n• Tên nhóm: {client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {}).get('name', 'None')}\n• ID: {group_id}"
            for i, group_id in enumerate(unapproved_groups)
        )
        success_message = group_list if unapproved_groups else "Tất cả các nhóm đã được duyệt."
    
    else:
        success_message = ("• Vui lòng nhập lệnh đầy đủ: \n"
                           "`autosend duyet`,\n"
                           "`autosend ban`,\n"
                           "`autosendduyetall`,\n"
                           "`autosend banall`,\n"
                           "`autosend listduyet`,\n"
                           "`autosend list-approved`,\n"
                           "`autosend banid`,\n"
                           "`autosend duyetid`")

    client.replyMessage(Message(text=success_message), message_object, thread_id, thread_type, ttl=30000)

def get_tmii():
    return {
        'autosend': handle_duyetbox_command
    }
