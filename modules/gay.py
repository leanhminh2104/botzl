from zlapi.models import MultiMsgStyle, Mention,MessageStyle
from zlapi.models import Message
import random
from config import *

des = {
    'version': "1.0.0",
    'credits': "DuongNgocc",
    'description': "check ti le dong tinh cua nam"
}
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_gay_command(message, message_object, thread_id, thread_type, author_id, client):
            if not check_group_access(thread_id, author_id):
               return

            if not message_object.mentions:
                client.replyMessage(Message(text='Vui lòng đề cập đến một người dùng.'), message_object, thread_id=thread_id, thread_type=thread_id)
            else:
                user_id = message_object.mentions[0]['uid']
                probability = random.randint(0, 100)  
                response = f"• Khả năng <@{user_id}> bị gay là {probability}%."
            styles = MultiMsgStyle([
                MessageStyle(offset=0, length=2, style="color", color="#a24ffb", auto_format=False),
                MessageStyle(offset=2, length=len(response)-2, style="color", color="#ffaf00", auto_format=False),
                MessageStyle(offset=0, length=len(response), style="font", size="13", auto_format=False)
            ])
            mention = Mention(user_id, length=len(f"<@{user_id}>"), offset=response.index(f"<@{user_id}>"))
                
            client.replyMessage(Message(text=response, mention=mention,style=styles), message_object, thread_id=thread_id, thread_type=thread_type)
def get_tmii():
    return {
        'gay': handle_gay_command
    }