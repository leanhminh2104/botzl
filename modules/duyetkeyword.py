import json
import os
from zlapi.models import *
from config import *
import time

des = {
    'version': "1.0.0",
    'credits': "LAMDev",
    'description': "Quản lý danh sách từ khóa: thêm, xóa, xem danh sách từ khóa."
}

keyword_FILE = 'modules/cache/keyword.json'
ADMINLAM = '3704058103894860815, 776103656827420589'

# Kiểm tra quyền admin
def is_admin(author_id):
    admin_ids = [admin_id.strip() for admin_id in ADMINLAM.split(',')]
    print(f"Checking admin status for {author_id}. Admin IDs: {admin_ids}")  # Log check
    return str(author_id).strip() in admin_ids

# Tải danh sách từ khóa
def load_keyword():
    if not os.path.exists(keyword_FILE):
        print("Keyword file not found, returning empty list.")  # Log missing file
        return []
    with open(keyword_FILE, 'r') as f:
        try:
            data = json.load(f)
            print(f"Loaded keywords: {data}")  # Log loaded data
            return data if isinstance(data, list) else []
        except json.JSONDecodeError as e:
            print(f"Error loading keyword file: {e}")  # Log JSON decode error
            return []

# Lưu danh sách từ khóa
def save_keyword(data):
    with open(keyword_FILE, 'w') as f:
        try:
            json.dump(data, f, indent=4)
            print(f"Saved keywords: {data}")  # Log saved data
        except Exception as e:
            print(f"Error saving keyword file: {e}")  # Log saving error

# Xử lý lệnh keyword
def handle_keyword_command(message, message_object, thread_id, thread_type, author_id, client):
    print(f"Received message: {message}")  # Log received message
    print(f"Message Object: {message_object}")  # Log toàn bộ message_object
    text = message.split()
    
    if len(text) < 2:
        error_message = ("• Vui lòng nhập lệnh đầy đủ:\n"
                         "`keyword add <từ>`\n"
                         "`keyword remove <từ>`\n"
                         "`keyword list`\n"
                         "`keyword reply`")
        client.replyMessage(Message(text=error_message), message_object, thread_id, thread_type, ttl=30000)
        return

    action = text[1].lower()
    keywords = load_keyword()

    if action == 'add':
        if not is_admin(author_id):
            client.replyMessage(Message(text="• Bạn không có quyền thêm từ khóa."), message_object, thread_id, thread_type, ttl=30000)
            return

        if len(text) < 3:
            client.replyMessage(Message(text="• Vui lòng nhập từ khóa cần thêm."), message_object, thread_id, thread_type, ttl=30000)
            return
        keyword = " ".join(text[2:]).strip().lower()

        if keyword in keywords:
            client.replyMessage(Message(text=f"• Từ khóa '{keyword}' đã tồn tại."), message_object, thread_id, thread_type, ttl=30000)
        else:
            keywords.append(keyword)
            save_keyword(keywords)
            client.replyMessage(Message(text=f"• Đã thêm từ khóa '{keyword}' thành công."), message_object, thread_id, thread_type, ttl=30000)

    elif action == 'remove':
        if not is_admin(author_id):
            client.replyMessage(Message(text="• Bạn không có quyền xóa từ khóa."), message_object, thread_id, thread_type, ttl=30000)
            return
        if len(text) < 3:
            client.replyMessage(Message(text="• Vui lòng nhập từ khóa cần xóa."), message_object, thread_id, thread_type, ttl=30000)
            return
        keyword = " ".join(text[2:]).strip().lower()
        if keyword in keywords:
            keywords.remove(keyword)
            save_keyword(keywords)
            client.replyMessage(Message(text=f"• Đã xóa từ khóa '{keyword}' thành công."), message_object, thread_id, thread_type, ttl=30000)
        else:
            client.replyMessage(Message(text=f"• Không tìm thấy từ khóa '{keyword}'."), message_object, thread_id, thread_type, ttl=30000)

    elif action == 'list':
        if not keywords:
            client.replyMessage(Message(text="• Danh sách từ khóa đang trống."), message_object, thread_id, thread_type, ttl=30000)
        else:
            keyword_list = "\n".join(f"{i+1}. {kw}" for i, kw in enumerate(keywords))
            client.replyMessage(Message(text=f"• Danh sách từ khóa:\n{keyword_list}"), message_object, thread_id, thread_type, ttl=60000)

    elif action == 'reply':
        if not is_admin(author_id):
            client.replyMessage(Message(text="• Bạn không có quyền thêm từ khóa từ tin nhắn trả lời."), message_object, thread_id, thread_type, ttl=30000)
            return
        
        # Kiểm tra xem tin nhắn có phải là một tin nhắn trả lời hay không
        if 'quote' not in message_object or not message_object['quote'] or 'msg' not in message_object['quote']:
            client.replyMessage(Message(text="• Bạn phải trả lời một tin nhắn để thêm từ khóa."), message_object, thread_id, thread_type, ttl=30000)
            return
        
        # Lấy tin nhắn trả lời và kiểm tra từ khóa
        reply_message = message_object['quote']
        print(f"Reply Message: {reply_message}")  # Log tin nhắn trả lời
        keyword = reply_message['msg'].strip().lower()
        
        # Kiểm tra xem từ khóa đã tồn tại chưa
        if keyword in keywords:
            client.replyMessage(Message(text=f"• Từ khóa '{keyword}' đã tồn tại."), message_object, thread_id, thread_type, ttl=30000)
        else:
            keywords.append(keyword)
            save_keyword(keywords)
            client.replyMessage(Message(text=f"• Đã thêm từ khóa '{keyword}' từ tin nhắn trả lời."), message_object, thread_id, thread_type, ttl=30000)

    else:
        error_message = ("• Vui lòng nhập đúng cú pháp:\n"
                         "`keyword add <từ>`\n"
                         "`keyword remove <từ>`\n"
                         "`keyword list`\n"
                         "`keyword reply`")
        client.replyMessage(Message(text=error_message), message_object, thread_id, thread_type, ttl=30000)

def get_tmii():
    return {
        'keyword': handle_keyword_command
    }
