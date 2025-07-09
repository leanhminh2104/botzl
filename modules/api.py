import json
import os
from zlapi.models import Message
from config import *  # Giả sử đây là nơi bạn chứa thông tin cấu hình như ALLOW_GR và ADMIN.

des = {
    'version': "1.0.0",
    'credits': "LAMDev",
    'description': "Thêm và Check api"
}

api = "Api/"

# Kiểm tra và tạo thư mục nếu chưa có
if not os.path.exists(api):
    os.makedirs(api)

def check_group_access(thread_id, sender_id):
    """
    Kiểm tra quyền truy cập nhóm:
    - Nếu nhóm không nằm trong danh sách ALLOW_GR hoặc người gửi không phải ADMIN, sẽ không trả lời.
    """
    if sender_id not in ADMIN:
        return False
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
    return True

def handle_api_command(args, message_object, thread_id, thread_type, author_id, client):
    """
    Hàm xử lý các lệnh API: thêm link vào tệp hoặc kiểm tra số lượng link trong tệp.
    """
    if not check_group_access(thread_id, author_id):
        return

    if author_id not in ADMIN:
        client.sendMessage(Message(text="Bạn không có quyền thực hiện hành động này!"), thread_id, thread_type)
        return

    args = args.split()
    if args[0] == '&api':
        args = args[1:]
    
    if len(args) < 2:
        response_message = "Lệnh không hợp lệ. Vui lòng sử dụng: api add <tên_file> <link> hoặc api check <tên_file>"
    else:
        command = args[0]
        file_name = args[1]
        file_path = os.path.join(api, f"{file_name}.json")

        print(f"DEBUG: command = {command}, file_name = {file_name}, file_path = {file_path}")

        if command == "add" and len(args) == 3:
            link = args[2]
            data = []

            # Kiểm tra tệp đã tồn tại chưa
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                except json.JSONDecodeError:
                    response_message = f"Lỗi: Không thể đọc tệp {file_name}.json."
                    client.sendMessage(Message(text=response_message), thread_id, thread_type)
                    return
            # Thêm link vào danh sách
            data.append(link)
            try:
                with open(file_path, 'w') as file:
                    json.dump(data, file, indent=4)
                response_message = f"Đã thêm link vào {file_name}.json. Tổng cộng: {len(data)} link."
            except IOError:
                response_message = f"Lỗi: Không thể ghi vào tệp {file_name}.json."

        elif command == "check" and len(args) == 2:
            # Kiểm tra tệp có tồn tại không
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                    response_message = f"{file_name}.json hiện có {len(data)} link."
                except json.JSONDecodeError:
                    response_message = f"Lỗi: Không thể đọc tệp {file_name}.json."
            else:
                response_message = f"Tệp {file_name}.json không tồn tại."
        else:
            response_message = "Lệnh không hợp lệ hoặc thiếu tham số."

    client.sendMessage(Message(text=response_message), thread_id, thread_type)

def get_tmii():
    """
    Trả về danh sách các lệnh API
    """
    return {
        'api': handle_api_command
    }
