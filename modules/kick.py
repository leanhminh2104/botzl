from zlapi.models import Message, Mention, MultiMsgStyle, MessageStyle
from config import *
ADMIN_ID = ADMIN

des = {
    'version': "1.0.1",
    'credits': "DuongNgocc",
    'description': "kick thành viên trong nhóm"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_kick_command(message, message_object, thread_id, thread_type, author_id, client):
        if not check_group_access(thread_id, author_id):
            return
        if author_id not in ADMIN:
				
            msg = "• Bạn Không Có Quyền! Chỉ có admin mới có thể sử dụng được lệnh này."
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
                MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
                MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
            ])
				
            client.replyMessage(Message(text=msg, style=styles),message_object, thread_id, thread_type,ttl=20000)
            return

			
        if message_object.mentions:
            user_id = message_object.mentions[0].uid
			
        elif message_object.quote:
            user_id = str(message_object.quote.ownerId)
		

        else:
				
            msg = f"• Không thể kick người dùng vì cú pháp không hợp lệ!\n\n| Command: kick <tag/reply/id>"
            example_usage = msg.splitlines()[-1]
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
                MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
                MessageStyle(offset=msg.find(example_usage), length=11, style="bold", auto_format=False),
                MessageStyle(offset=msg.find(example_usage), length=1, style="color", color="#585b70", auto_format=False),
                MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
            ])
            
            client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type,ttl=20000)
            return
			
        group_data = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]
        admins = group_data.adminIds
        owners = group_data.creatorId
	
        if client.uid not in admins and client.uid != owners:
            
            msg = f"• Bot không thể kick người dùng vì không có quyền! Vui lòng cấp key cho bot để có thể kick thành viên nhóm."
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#fab387", auto_format=False),
                MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
                MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
            ])
            
            client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type,ttl=20000)
        
        elif user_id in admins or user_id == owners:

            if user_id in admins:
                msg = "• Không thể kick key bạc của nhóm!"
            elif user_id == owners:
                msg = "• Không thể kick key vàng của nhóm!"
            
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
                MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
                MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
            ])
            
            client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type,ttl=20000)
            
        else:

            client.blockUsersInGroup(user_id, thread_id)
            msg = f"• Đã kick @mention khỏi nhóm."
            offset_mention = msg.find("@mention")
            mention = Mention(user_id, offset=offset_mention, length=8)
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#a6e3a1", auto_format=False),
                MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
                MessageStyle(offset=offset_mention, length=8, style="color", color="#89b4fa", auto_format=False),
                MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
            ])
            
            client.send(Message(text=msg, style=styles, mention=mention), thread_id, thread_type,ttl=20000)
def get_tmii():
    return {
        'kick': handle_kick_command
    }