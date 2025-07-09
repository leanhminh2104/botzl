import os
import datetime
from zlapi import ZaloAPI
from zlapi.models import Message
from zlapi import ZaloAPIException
from config import *

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "Lệnh này cung cấp thông tin chi tiết về các lệnh khác."
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def in4(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    msg_error = "• Cú pháp không chính xác.\nVí dụ: ..in4, ..in4 @mention, hoặc ..in4 số điện thoại"

    try:
        # Xác định user_id
        phoneNumber = ""
        
        # Nếu là mention
        if message_object.mentions:
            user_id = message_object.mentions[0]['uid']
        
        # Nếu là số điện thoại
        elif message[5:].strip().isnumeric():
            phoneNumber = message[5:].strip()
            try:
                # Thử fetch thông tin bằng số điện thoại
                info_phone = client.fetchPhoneNumber(phoneNumber, language='vi')
                
                # Kiểm tra kết quả trả về
                if isinstance(info_phone, dict) and 'error_code' in info_phone:
                    client.replyMessage(
                        Message(text=f"• Lỗi: {info_phone.get('error_msg', 'Không xác định')}"), 
                        message_object, thread_id, thread_type,
                        ttl=3000
                    )
                    return
                
                # Lấy user_id từ thông tin điện thoại
                user_id = info_phone.get('uid')
                
            except ZaloAPIException as zae:
                client.replyMessage(
                    Message(text=f"• Lỗi ZaloAPI: {str(zae)}"), 
                    message_object, thread_id, thread_type,
                    ttl=3000
                )
                return
            except Exception as e:
                client.replyMessage(
                    Message(text=f"• Lỗi tra cứu: {str(e)}"), 
                    message_object, thread_id, thread_type,
                    ttl=3000
                )
                return
        
        # Nếu không có mention hay số điện thoại
        elif message.strip() == ">in4":
            user_id = author_id
        else:
            client.replyMessage(
                Message(text=msg_error), 
                message_object, thread_id, thread_type,
                ttl=3000
            )
            return

        # Lấy thông tin người dùng
        try:
            # In ra để debug
            print(f"Fetching user info for ID: {user_id}")
            
            # Gọi fetchUserInfo
            user_info = client.fetchUserInfo(user_id)
            
            # In ra để kiểm tra dữ liệu
            print(f"User Info: {user_info}")
            
            # Trích xuất thông tin
            info = user_info.changed_profiles or user_info.unchanged_profiles
            
            # Kiểm tra nếu không có thông tin
            if not info:
                client.replyMessage(
                    Message(text="• Không tìm thấy thông tin người dùng"), 
                    message_object, thread_id, thread_type,
                    ttl=3000
                )
                return

            # Lấy thông tin chi tiết
            info = info[str(user_id)]
            
            # Xây dựng tin nhắn
            msg_parts = [
                f"• User ID: {info.get('userId', 'Không xác định')}",
                f"• Tên Zalo: {(info.get('zaloName', '')[:30] + '...') if len(info.get('zaloName', '')) > 30 else info.get('zaloName', 'Không có')}",
                f"• Giới tính: {'Nam' if info.get('gender') == 0 else 'Nữ' if info.get('gender') == 1 else 'Không xác định'}",
            ]

            # Thêm các thông tin khác
            if info.get('status'):
                msg_parts.append(f"• Trạng thái: {info['status']}")
            
            # Thêm các trường thông tin
            extra_info = [
                (f"• Số điện thoại: {phoneNumber}" if phoneNumber else "• Số điện thoại: Không có"),
                f"• Tài khoản Business: {'Có' if info.get('bizPkg', {}).get('label') else 'Không'}",
                f"• Hoạt động cuối: {datetime.datetime.fromtimestamp(info.get('lastActionTime', 0)/1000).strftime('%H:%M %d/%m/%Y')}",
                f"• Ngày tạo: {datetime.datetime.fromtimestamp(info.get('createdTs', 0)).strftime('%H:%M %d/%m/%Y')}",
                f"• Trạng thái tài khoản: {info.get('accountStatus', 'Không xác định')}"
            ]
            
            msg_parts.extend(extra_info)

            # Gửi tin nhắn
            client.replyMessage(
                Message(text="\n".join(msg_parts)), 
                message_object, thread_id, thread_type,
                ttl=300000
            )

        except ZaloAPIException as zae:
            print(f"ZaloAPI Error: {zae}")
            client.replyMessage(
                Message(text=f"• Lỗi ZaloAPI: {str(zae)}"), 
                message_object, thread_id, thread_type,
                ttl=3000
            )
        except Exception as e:
            print(f"Lỗi không xác định: {e}")
            client.replyMessage(
                Message(text=f"• Lỗi không xác định: {str(e)}"), 
                message_object, thread_id, thread_type,
                ttl=3000
            )

    except Exception as e:
        print(f"Lỗi chung: {e}")
        client.replyMessage(
            Message(text="• Đã xảy ra lỗi không mong muốn"), 
            message_object, thread_id, thread_type
        )

def get_tmii():
    return {
        'in4': in4
    }