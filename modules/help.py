import os
from zlapi.models import Message
import importlib
from config import *

# Thông tin về lệnh 'help'
des = {
    'version': "1.0.1",
    'credits': "LAMDev",
    'description': "Lệnh này cung cấp thông tin chi tiết về các lệnh khác."
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
# Hàm lấy thông tin về tất cả các lệnh trong thư mục 'modules'
def get_all_tmii_with_info():
    tmii_info = {}

    for module_name in os.listdir('modules'):
        if module_name.endswith('.py') and module_name != '__init__.py':
            module_path = f'modules.{module_name[:-3]}'
            module = importlib.import_module(module_path)

            if hasattr(module, 'des'):
                des = getattr(module, 'des')
                version = des.get('version', 'Chưa có thông tin')
                credits = des.get('credits', 'Chưa có thông tin')
                description = des.get('description', 'Chưa có thông tin')
                tmii_info[module_name[:-3]] = (version, credits, description)

    return tmii_info

def paginate_commands(tmii_info, page=1, page_size=5):
    total_pages = (len(tmii_info) + page_size - 1) // page_size
    if page < 1 or page > total_pages:
        return None, total_pages

    start = (page - 1) * page_size
    end = start + page_size

    commands_on_page = list(tmii_info.items())[start:end]

    return commands_on_page, total_pages

def handle_help_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    command_parts = message.split()
    
    tmii_info = get_all_tmii_with_info()

    if len(command_parts) > 1:
        requested_command = command_parts[1].lower()
        
        if requested_command in tmii_info:
            version, credits, description = tmii_info[requested_command]
            single_command_help = f"• Tên lệnh: {requested_command}\n• Phiên bản: {version}\n• Credits: {credits}\n• Mô tả: {description}"
            message_to_send = Message(text=single_command_help)
            client.replyMessage(message_to_send, message_object, thread_id, thread_type)
            return
        elif command_parts[1].isdigit():
            page = int(command_parts[1])
        else:
            message_to_send = Message(text=f"Không tìm thấy lệnh '{requested_command}' trong hệ thống.")
            client.replyMessage(message_to_send, message_object, thread_id, thread_type)
            return
    else:
        page = 1

    commands_on_page, total_pages = paginate_commands(tmii_info, page)

    if commands_on_page is None:
        help_message = f"Trang {page} không hợp lệ. Tổng số trang hiện có: {total_pages}."
    else:
        help_message_lines = [f"Tổng số lệnh bot hiện tại: {len(tmii_info)} lệnh\n"]
        for i, (name, (version, credits, description)) in enumerate(commands_on_page, (page - 1) * 5 + 1):
            help_message_lines.append(f"{i}:\n• Tên lệnh: {name}\n• Phiên bản: {version}\n• Credits: {credits}\n• Mô tả: {description}\n")
            help_message_lines.append(f"\n> Để xem thông tin các lệnh khác, vui lòng dùng {PREFIX}help + số trang\n> Ví dụ: {PREFIX}help 2\n> Trang số: {page}/{total_pages}")
            help_message = "\n".join(help_message_lines)

    message_to_send = Message(text=help_message)
    client.replyMessage(message_to_send, message_object, thread_id, thread_type,ttl=60000)
# Hàm lấy các lệnh bot
def get_tmii():
    return {
        'help': handle_help_command
    }
