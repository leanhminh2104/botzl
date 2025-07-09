import threading
from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES, BOT_ID, PREFIX
from zlapi import ZaloAPI
from zlapi.models import Message
from colorama import Fore, Style, init
import time
from datetime import datetime
import json
import os
from zlapi import *
from zlapi.models import *
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
import requests
from tmii import CommandHandler
CACHE_FILE = 'modules/cache/keyword.json'
background_path = 'background_image.jpg'
# Global variables
current_time = datetime.now()
formatted_time = current_time.strftime("%d/%m/%Y [%H:%M:%S]")
##### hàm mute


###
def delete_file(filename):
    try:
        os.remove(filename)
    except OSError as e:
        print(f"Error deleting file {filename}: {e}")

def make_round_avatar(avatar):
    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
    round_avatar = Image.new('RGBA', avatar.size)
    round_avatar.paste(avatar, (0, 0), mask)
    return round_avatar

def initialize_group_info(bot, allowed_thread_ids):
    for thread_id in allowed_thread_ids:
        group_info = bot.fetchGroupInfo(thread_id).gridInfoMap.get(thread_id, None)
        if group_info:
            bot.group_info_cache[thread_id] = {
                "name": group_info['name'],
                "member_list": group_info['memVerList'],
                "total_member": group_info['totalMember']
            }
        else:
            print(f"Bỏ qua nhóm {thread_id}")

def check_member_changes(bot, thread_id):
    current_group_info = bot.fetchGroupInfo(thread_id).gridInfoMap.get(thread_id, None)
    cached_group_info = bot.group_info_cache.get(thread_id, None)
    if not cached_group_info or not current_group_info:
        return [], []
    old_members = set([member.split('_')[0] for member in cached_group_info["member_list"]])
    new_members = set([member.split('_')[0] for member in current_group_info['memVerList']])
    joined_members = new_members - old_members
    left_members = old_members - new_members
    bot.group_info_cache[thread_id] = {
        "name": current_group_info['name'],
        "member_list": current_group_info['memVerList'],
        "total_member": current_group_info['totalMember']
    }
    return joined_members, left_members

def create_welcome_image_with_avatar(member_name, avatar_url, font_folder, group_name, member_number, background_path=None):
    if not os.path.exists(font_folder):
        os.makedirs(font_folder)
    
    # Create base image with wider dimensions
    width, height = 800, 400
    background = Image.new("RGB", (width, height))
    
    # Load and apply background
    try:
        if background_path and os.path.exists(background_path):
            bg = Image.open(background_path).convert("RGB")
        else:
            bg = Image.open("background.jpg").convert("RGB")
        bg = bg.resize((width, height))
        background.paste(bg, (0, 0))
    except:
        # Fallback to dark blue gradient
        draw = ImageDraw.Draw(background)
        for y in range(height):
            r = int(0 * (1 - y/height))
            g = int(20 * (1 - y/height))
            b = int(50 * (1 - y/height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    draw = ImageDraw.Draw(background)
    
    # Create semi-transparent card
    card_width = 600
    card_height = 300
    card_x = (width - card_width) // 2
    card_y = (height - card_height) // 2
    
    # Main overlay with increased transparency
    overlay = Image.new("RGBA", (card_width, card_height), (0, 0, 0, 120))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=5))
    
    # Create rounded corners mask
    mask = Image.new("L", (card_width, card_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (card_width, card_height)], radius=20, fill=255)
    
    # Apply overlay
    background.paste(overlay, (card_x, card_y), mask)
    
    # Create text area with separate transparency
    text_area = Image.new("RGBA", (card_width - 160, card_height), (0, 0, 0, 80))
    text_mask = Image.new("L", (card_width - 160, card_height), 0)
    text_mask_draw = ImageDraw.Draw(text_mask)
    text_mask_draw.rounded_rectangle([(0, 0), (card_width - 160, card_height)], radius=15, fill=255)
    background.paste(text_area, (card_x + 160, card_y), text_mask)

    # Load fonts
    try:
        title_font = ImageFont.truetype(os.path.join(font_folder, "arial.ttf"), 35)
        regular_font = ImageFont.truetype(os.path.join(font_folder, "arial.ttf"), 30)
    except:
        title_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()

    # Avatar section
    try:
        avatar_size = 100
        avatar_response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
        avatar = avatar.resize((avatar_size, avatar_size))
        
        frame_size = avatar_size + 10
        frame = Image.new('RGBA', (frame_size, frame_size))
        frame_draw = ImageDraw.Draw(frame)
        frame_draw.ellipse([0, 0, frame_size, frame_size], fill=(255, 165, 0, 255))
        
        mask = Image.new('L', (avatar_size, avatar_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, avatar_size, avatar_size], fill=255)
        
        avatar_x = card_x + 50
        avatar_y = card_y + 50
        
        background.paste(frame, (avatar_x - 5, avatar_y - 5), frame)
        background.paste(avatar, (avatar_x, avatar_y), mask)
    except Exception as e:
        print(f"Error processing avatar: {e}")

    # Text content
    text_x = card_x + 200
    text_y = card_y + 40
    
    draw.text((text_x, text_y), f"Name: {member_name}", font=regular_font, fill=(255, 255, 255))
    draw.text((text_x, text_y + 30), f"Second Member: {member_number}", font=regular_font, fill=(255, 255, 255))
    
    draw.text((text_x, text_y + 70), "Hello And Hi:", font=title_font, fill=(0, 255, 255))
    draw.text((text_x, text_y + 110), f"•Welcome To: {member_name}", font=regular_font, fill=(255, 255, 255))
    draw.text((text_x, text_y + 150), f"Come With: {group_name}", font=regular_font, fill=(255, 255, 255))
    draw.text((text_x, text_y + 190), "A Place to Relax", font=regular_font, fill=(255, 255, 255))
    draw.text((text_x, text_y + 220), "Have Fun With the Community", font=regular_font, fill=(255, 255, 255))

    output_path = "welcome.jpg"
    background.save(output_path, quality=95)
    return output_path

def create_farewell_image_with_avatar(member_name, avatar_url, font_folder, group_name, background_path=None):
    if not os.path.exists(font_folder):
        os.makedirs(font_folder)
    
    width, height = 800, 400
    background = Image.new("RGB", (width, height))
    
    try:
        if background_path and os.path.exists(background_path):
            bg = Image.open(background_path).convert("RGB")
        else:
            bg = Image.open("background.jpg").convert("RGB")
        bg = bg.resize((width, height))
        background.paste(bg, (0, 0))
    except:
        draw = ImageDraw.Draw(background)
        for y in range(height):
            r = int(20 * (1 - y/height))
            g = int(0 * (1 - y/height))
            b = int(30 * (1 - y/height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    draw = ImageDraw.Draw(background)
    
    card_width = 600
    card_height = 300
    card_x = (width - card_width) // 2
    card_y = (height - card_height) // 2
    
    overlay = Image.new("RGBA", (card_width, card_height), (0, 0, 0, 120))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=1))
    
    mask = Image.new("L", (card_width, card_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (card_width, card_height)], radius=20, fill=255)
    
    background.paste(overlay, (card_x, card_y), mask)
    
    text_area = Image.new("RGBA", (card_width - 160, card_height), (0, 0, 0, 80))
    text_mask = Image.new("L", (card_width - 160, card_height), 0)
    text_mask_draw = ImageDraw.Draw(text_mask)
    text_mask_draw.rounded_rectangle([(0, 0), (card_width - 160, card_height)], radius=15, fill=255)
    background.paste(text_area, (card_x + 160, card_y), text_mask)

    try:
        title_font = ImageFont.truetype(os.path.join(font_folder, "arial.ttf"), 35)
        regular_font = ImageFont.truetype(os.path.join(font_folder, "arial.ttf"), 30)
    except:
        title_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()

    try:
        avatar_size = 100
        avatar_response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
        avatar = avatar.resize((avatar_size, avatar_size))
        
        frame_size = avatar_size + 10
        frame = Image.new('RGBA', (frame_size, frame_size))
        frame_draw = ImageDraw.Draw(frame)
        frame_draw.ellipse([0, 0, frame_size, frame_size], fill=(255, 69, 0, 255))
        
        mask = Image.new('L', (avatar_size, avatar_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, avatar_size, avatar_size], fill=255)
        
        avatar_x = card_x + 50
        avatar_y = card_y + 50
        
        background.paste(frame, (avatar_x - 5, avatar_y - 5), frame)
        background.paste(avatar, (avatar_x, avatar_y), mask)
    except Exception as e:
        print(f"Error processing avatar: {e}")

    text_x = card_x + 200
    text_y = card_y + 40
    
    draw.text((text_x, text_y+20), f"Name: {member_name}", font=regular_font, fill=(255, 255, 255))
    
    draw.text((text_x, text_y + 80), "Farewell Message:", font=title_font, fill=(255, 69, 0))
    draw.text((text_x, text_y + 120), f"Good Bye: {member_name}", font=regular_font, fill=(255, 255, 255))
    draw.text((text_x, text_y + 160), f"Out The Group: {group_name}", font=regular_font, fill=(255, 255, 255))
    draw.text((text_x, text_y + 200), "See You Again 💔", font=regular_font, fill=(255, 255, 255))

    output_path = "farewell.jpg"
    background.save(output_path, quality=95)
    return output_path

# Update the handle_group_member function to accept background path
def handle_group_member(bot, message_object, author_id, thread_id, thread_type, background_path=None):
    joined_members, left_members = check_member_changes(bot, thread_id)
    if joined_members:
        for member_id in joined_members:
            try:
                member_info = bot.fetchUserInfo(member_id).changed_profiles[member_id]
                welcome_image_path = create_welcome_image_with_avatar(
                    member_info.displayName,
                    member_info.avatar,
                    "font",
                    bot.group_info_cache[thread_id]['name'],
                    bot.group_info_cache[thread_id]['total_member'],
                    background_path
                )
                messagesend = Message(
                    text=f"•Welcome To: {member_info.displayName} \n"
                         f"•Join Group: {bot.group_info_cache[thread_id]['name']} \n"
                         f"•Time of Joining: {formatted_time} \n"
                         f"•Number of Members: {bot.group_info_cache[thread_id]['total_member']}"
                )
                bot.sendLocalImage(welcome_image_path, thread_id, thread_type, message=messagesend, width=600, height=300,ttl=120000)
                delete_file(welcome_image_path)
            except Exception as e:
                print(f"Lỗi khi xử lý thành viên mới {member_id}: {e}")

    if left_members:
        for member_id in left_members:
            try:
                member_info = bot.fetchUserInfo(member_id).changed_profiles[member_id]
                farewell_image_path = create_farewell_image_with_avatar(
                    member_info.displayName,
                    member_info.avatar,
                    "font",
                    bot.group_info_cache[thread_id]['name'],
                    background_path
                )
                messagesend = Message(
                    text=f"•Good Bye: {member_info.displayName} 🤧 \n"
                         f"•Time Out of Group: {formatted_time} \n"
                         f"•Number of Remaining Members: {bot.group_info_cache[thread_id]['total_member']}"
                )
                bot.sendLocalImage(farewell_image_path, thread_id, thread_type, message=messagesend, width=600, height=300,ttl=120000)
                delete_file(farewell_image_path)
            except Exception as e:
                print(f"Lỗi khi xử lý thành viên rời {member_id}: {e}")


class Client(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies, bot_id):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        self.del_enabled = {}
        self.default_del_enabled = True
        self.bot_id = bot_id
        self.command_handler = CommandHandler(self)
        self.group_info_cache = {}
        self.background_path = background_path
        all_group = self.fetchAllGroups()
        allowed_thread_ids = list(all_group.gridVerMap.keys())
        initialize_group_info(self, allowed_thread_ids)
        self.start_member_check_thread(allowed_thread_ids)
    
    def start_member_check_thread(self, allowed_thread_ids):
        def check_members_loop():
            while True:
                for thread_id in allowed_thread_ids:
                    handle_group_member(self, None, None, thread_id, ThreadType.GROUP, self.background_path)
                time.sleep(1)

        thread = threading.Thread(target=check_members_loop)
        thread.daemon = True
        thread.start()

    def handle_message(self, mid, author_id, message, message_object, thread_id, thread_type):
        try:
            message_text = message.text if isinstance(message, Message) else str(message)

            # Log message details
            current_time = time.strftime("%H:%M:%S - %d/%m/%Y", time.localtime())
            print(f"------------------------------\n"
                  f"Message: {message_text}\n"
                  f"Author ID: {author_id}\n"
                  f"Thread ID: {thread_id}\n"
                  f"Thread Type: {thread_type}\n"
                  f"Timestamp: {current_time}\n"
                  f"------------------------------")

            if isinstance(message, str):
                self.command_handler.handle_command(
                    message, author_id, message_object, thread_id, thread_type
                )
            if self.del_enabled.get(thread_id, self.default_del_enabled):
                self.check_and_delete_links(author_id, message_text, message_object, thread_id)

        except Exception as e:
            print(f"Error handling message: {e}")
            
    
    #def check_and_delete_links(self, author_id, message_text, message_object, thread_id):
    #    contains_link = ".Com" in message_text or "t.me" in message_text or "zalo.me" in message_text or ".Net" in message_text or ".Vn" in message_text or ".Site" in message_text or "lol" in message_text or "cc" in message_text or "lon" in message_text or ".VN" in message_text or "COM" in message_text or ".NET" in message_text or ".ME" in message_text or "lỏ" in message_text or "Lol" in message_text or "Cc" in message_text or "Lon" in message_text or "lol" in message_text or "cc" in message_text or "lon" in message_text or ".VN" in message_text or "COM" in message_text or ".NET" in message_text or ".ME" in message_text or "lồn" in message_text or "cặc" in message_text or "Lồn" in message_text or "Cặc" in message_text
	#	
     #   if contains_link and author_id != self.bot_id:
      #      try:
    ##            self.deleteGroupMsg(
     #               msgId=message_object.msgId,
     #               ownerId=author_id,
      #              clientMsgId=message_object.cliMsgId,
       #             groupId=thread_id
        #        )
         #       print(f"Deleted a message containing a link from {author_id} in group {thread_id}")
          #  except Exception as e:
           #     print(f"Error while deleting message: {e}")

     ## hàm xóa theo từ khóa
    def load_keywords(self):
        """Đọc danh sách từ khóa từ file JSON"""
        if not os.path.exists(CACHE_FILE):
            return []
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [kw.lower() for kw in data if isinstance(kw, str)]
        except json.JSONDecodeError:
            return []

    def check_and_delete_links(self, author_id, message_text, message_object, thread_id):
        # Tải bộ từ khóa
        keywords = self.load_keywords()
        text = (message_text or '').lower()
        # Kiểm tra xem có bất kỳ từ khóa nào trong text
        hit = next((kw for kw in keywords if kw in text), None)
        if hit and author_id != self.bot_id:
            try:
                self.deleteGroupMsg(
                    msgId=message_object.msgId,
                    ownerId=author_id,
                    clientMsgId=message_object.cliMsgId,
                    groupId=thread_id
                )
                print(f"Deleted message containing '{hit}' from {author_id} in group {thread_id}")
            except Exception as e:
                print(f"Error while deleting message: {e}")
##################################

    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        threading.Thread(target=self.handle_message, args=(mid, author_id, message, message_object, thread_id, thread_type)).start()

if __name__ == "__main__":
    client = Client(API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES, BOT_ID)
    client.listen(run_forever=True, type='websocket')
