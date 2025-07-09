from zlapi.models import Message
import json
import random
from zlapi.models import *
from config import *

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "Gửi tin nhắn có hiệu ứng gradient màu trên nội dung tin nhắn"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '{:02x}{:02x}{:02x}'.format(*rgb_color)

def generate_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def generate_gradient_colors(length):
    start_color = generate_random_color()
    end_color = generate_random_color()
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)

    colors = []
    for i in range(length):
        interpolated_color = (
            int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (length - 1)),
            int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (length - 1)),
            int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (length - 1))
        )
        colors.append(rgb_to_hex(interpolated_color))
    
    return colors

def create_rainbow_params(text, size=20):
    styles = []
    colors = generate_gradient_colors(len(text))
    
    for i, color in enumerate(colors):
        styles.append({"start": i, "len": 1, "st": f"c_{color}"})
    
    params = {"styles": styles, "ver": 0}
    return json.dumps(params)

def sendMessageColor(client, custom_text, message_object, thread_id, thread_type):
    if not check_group_access(thread_id, author_id):
        return
    stype = create_rainbow_params(custom_text)
    mes = Message(
        text=custom_text,
        style=stype
    )
    client.send(mes, thread_id, thread_type)

def replyMessageColor(client, custom_text, message_object, thread_id, thread_type):
    if not check_group_access(thread_id, author_id):
        return
    stype = create_rainbow_params(custom_text)
    mes = Message(
        text=custom_text,
        style=stype
    )
    client.replyMessage(mes, message_object, thread_id=thread_id, thread_type=thread_type)

def handle_text_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    content = message.split(' ', 1)[1].strip() if len(message.split(' ', 1)) > 1 else ""
    
    if content:
        custom_text = content.strip()
        replyMessageColor(client, custom_text, message_object, thread_id, thread_type)

def get_tmii():
    return {
        'text': handle_text_command
    }
