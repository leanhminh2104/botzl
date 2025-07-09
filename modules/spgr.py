from zlapi.models import Message, Mention, ZaloAPIException, ThreadType
from config import *
import time

des = {
    'version': "1.0.2",
    'credits': "DuongNgocc",
    'description': "Spam nhóm với nội dung tùy chỉnh và có thể dừng"
}

stop_spam = False  # Biến kiểm soát spam
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_spnhom_command(message, message_object, thread_id, thread_type, author_id, client):
    global stop_spam
    if not check_group_access(thread_id, author_id):
        return
    if author_id not in ADMIN:
        client.replyMessage(
            Message(text="🚫 Bạn không có quyền sử dụng lệnh này!"), 
            message_object, thread_id, thread_type
        )
        return
    
    try:
        parts = message.split(" ", 2)
        if len(parts) < 3:
            client.replyMessage(
                Message(text="⚠️ Vui lòng cung cấp link nhóm và nội dung spam!"), 
                message_object, thread_id, thread_type
            )
            return
            
        url = parts[1].strip()
        spam_text = parts[2].strip()
        
        if not url.startswith("https://zalo.me/"):
            client.replyMessage(
                Message(text="⛔ Link không hợp lệ! Link phải bắt đầu bằng https://zalo.me/"), 
                message_object, thread_id, thread_type
            )
            return
        
        join_result = client.joinGroup(url)
        if not join_result:
            raise ZaloAPIException("Không thể tham gia nhóm")
        
        group_info = client.getiGroup(url)
        if not isinstance(group_info, dict) or 'groupId' not in group_info:
            raise ZaloAPIException("Không thể lấy thông tin nhóm")
            
        group_id = group_info['groupId']
        
        stop_spam = False
        
        spam_count = 10  # Số lần spam
        for _ in range(spam_count):
            if stop_spam:
                break
            mention = Mention("-1", length=len(spam_text), offset=0)
            client.send(
                Message(text=spam_text, mention=mention),
                group_id, ThreadType.GROUP
            )
            time.sleep(0)
        
        while not stop_spam:
            mention = Mention("-1", length=len(spam_text), offset=0)
            client.send(
                Message(text=spam_text, mention=mention),
                group_id, ThreadType.GROUP
            )
            time.sleep(0)

        client.replyMessage(
            Message(text=f"🛑 Spam đã dừng!"),
            message_object, thread_id, thread_type
        )
        
    except ZaloAPIException as e:
        client.replyMessage(
            Message(text=f"❌ Lỗi API: {str(e)}"),
            message_object, thread_id, thread_type
        )
    except Exception as e:
        client.replyMessage(
            Message(text=f"❌ Lỗi: {str(e)}"),
            message_object, thread_id, thread_type
        )

def handle_stop_spam_command(message, message_object, thread_id, thread_type, author_id, client):
    global stop_spam
    if author_id not in ADMIN:
        client.replyMessage(
            Message(text="🚫 Bạn không có quyền sử dụng lệnh này!"), 
            message_object, thread_id, thread_type
        )
        return
    
    stop_spam = True
    client.replyMessage(
        Message(text="🛑 Đã gửi yêu cầu dừng spam!"),
        message_object, thread_id, thread_type
    )

def get_tmii():
    return {
        'spgr': handle_spnhom_command,
        'spgrstop': handle_stop_spam_command
    }
