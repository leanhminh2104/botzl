import os
import datetime
import requests
from zlapi import ZaloAPI
from zlapi.models import Message
from zlapi import ZaloAPIException
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import random
import colorsys
from config import *

des = {
    'version': "1.0.2",
    'credits': "DuongNgocc",
    'description': "Lệnh này cung cấp thông tin chi tiết về các lệnh khác."
}

def create_rounded_rectangle(draw, coords, radius, color):
    x1, y1, x2, y2 = coords
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=color)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=color)
    draw.ellipse([x1, y1, x1+2*radius, y1+2*radius], fill=color)
    draw.ellipse([x2-2*radius, y1, x2, y1+2*radius], fill=color)
    draw.ellipse([x1, y2-2*radius, x1+2*radius, y2], fill=color)
    draw.ellipse([x2-2*radius, y2-2*radius, x2, y2], fill=color)
def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def in4(message, message_object, thread_id, thread_type, author_id, client,font_folder='font'):
    if not check_group_access(thread_id, author_id):
        return

    output_path = f'{random.getrandbits(128)}output.png'

    msg_error = "• Cú pháp không chính xác.\nVí dụ: >in4, >in4 @mention, hoặc >in4 số điện thoại"

    try:
        # [Giữ nguyên phần xác định user_id như cũ]
        
        # Xác định user_id
        phoneNumber = ""
        
        # Nếu là mention
        if message_object.mentions:
            user_id = message_object.mentions[0]['uid']
        
        # Nếu là số điện thoại
        elif message[5:].strip().isnumeric():
            phoneNumber = message[5:].strip()
            try:
                info_phone = client.fetchPhoneNumber(phoneNumber, language='vi')
                
                if isinstance(info_phone, dict) and 'error_code' in info_phone:
                    client.replyMessage(
                        Message(text=f"• Lỗi: {info_phone.get('error_msg', 'Không xác định')}"), 
                        message_object, thread_id, thread_type
                    )
                    return
                
                user_id = info_phone.get('uid')
                
            except ZaloAPIException as zae:
                client.replyMessage(
                    Message(text=f"• Lỗi ZaloAPI: {str(zae)}"), 
                    message_object, thread_id, thread_type
                )
                return
            except Exception as e:
                client.replyMessage(
                    Message(text=f"• Lỗi tra cứu: {str(e)}"), 
                    message_object, thread_id, thread_type
                )
                return
        
        # Nếu không có mention hay số điện thoại
        elif message.strip() == ">in4":
            user_id = author_id
        else:
            client.replyMessage(
                Message(text=msg_error), 
                message_object, thread_id, thread_type
            )
            return
        try:
            print(f"Fetching user info for ID: {user_id}")
            
            user_info = client.fetchUserInfo(user_id)
            info = user_info.changed_profiles or user_info.unchanged_profiles
            print(user_info)
            if not info:
                client.replyMessage(
                    Message(text="• Không tìm thấy thông tin người dùng"), 
                    message_object, thread_id, thread_type
                )
                return

            info = info[str(user_id)]
            avatar_url = info.get('avatar')

            # Tạo ảnh nền
            image_url = "https://img.tripi.vn/cdn-cgi/image/width=700,height=700/https://gcs.tripi.vn/public-tripi/tripi-feed/img/474104FSP/hinh-anh-ban-dem-trong-your-name_082058116_thumb.jpg"
            response = requests.get(image_url)
            if response.status_code != 200:
                raise Exception("Không thể tải ảnh nền từ URL.")
            
            # Tạo ảnh với kích thước cố định và viền hồng
            background = Image.new('RGB', (1100, 600), (0, 0, 0))
            base_image = Image.open(BytesIO(response.content))
            base_image = base_image.resize((1100, 600))
            background.paste(base_image, (0, 0))

            # Tạo viền hồng
            border_color = (0, 255, 255) # Pink color
            border_width = 10
            draw = ImageDraw.Draw(background)
            draw.rectangle([0, 0, 1099, 599], outline=border_color, width=border_width)

            # Xử lý avatar
            avatar_size = (200, 200)
            if avatar_url:
                try:
                    avatar_response = requests.get(avatar_url)
                    if avatar_response.status_code == 200:
                        avatar = Image.open(BytesIO(avatar_response.content))
                        avatar = avatar.resize(avatar_size)
                        
                        # Tạo mask hình tròn cho avatar
                        mask = Image.new('L', avatar_size, 0)
                        mask_draw = ImageDraw.Draw(mask)
                        mask_draw.ellipse((0, 0) + avatar_size, fill=255)
                        
                        # Tạo viền hồng cho avatar
                        avatar_border = Image.new('RGBA', (220, 220), (255, 192, 203, 255))
                        avatar_border_mask = Image.new('L', (220, 220), 0)
                        avatar_border_draw = ImageDraw.Draw(avatar_border_mask)
                        avatar_border_draw.ellipse((0, 0, 219, 219), fill=255)
                        avatar_border.putalpha(avatar_border_mask)
                        
                        # Áp dụng mask cho avatar
                        output = Image.new('RGBA', avatar_size, (0, 0, 0, 0))
                        output.paste(avatar, (0, 0))
                        output.putalpha(mask)
                        
                        # Vị trí avatar (căn giữa theo chiều dọc)
                        avatar_x = 50
                        avatar_y = (background.height - 220) // 2
                        
                        # Paste viền avatar
                        background.paste(avatar_border, (avatar_x - 10, avatar_y - 10), avatar_border)
                        # Paste avatar
                        background.paste(output, (avatar_x, avatar_y), output)
                except Exception as e:
                    print(f"Error processing avatar: {e}")

            # Tạo khung thông tin với góc bo tròn
            info_box_color = (0, 0, 0, 180)  # Semi-transparent black
            info_box = Image.new('RGBA', (500, 300), info_box_color)
            info_box_draw = ImageDraw.Draw(info_box)
            
            # Vị trí khung thông tin
            info_x = 300
            info_y = (background.height - 300) // 2

            try:
                font = ImageFont.truetype(os.path.join(font_folder, "roboto.ttf"), size=24)
            except IOError:
                font = ImageFont.load_default()

            # Dữ liệu để hiển thị
            data = {
                "Tên": info.get('zaloName', 'Không có'),
                "Id": info.get('userId', 'Không xác định'),
                "Username": info.get('username', 'không xác định'),
                "Số điện thoại": phoneNumber or "Không có",
                "Giới tính": 'Nam' if info.get('gender') == 0 else 'Nữ' if info.get('gender') == 1 else 'Không xác định',
                "Sinh nhật": info.get('sdob', 'Không xác định'),
                "Ngày tạo tài khoản": datetime.datetime.fromtimestamp(info.get('createdTs', 0)).strftime('%H:%M %d/%m/%Y'),
                "Tiểu sử": info.get('status', 'Không có')
            }

            # Vẽ khung thông tin với màu trong suốt
            box_x = info_x + 20
            box_y = info_y + 20
            for key, value in data.items():
                text_color = (125, 249, 255)  # Pink color for labels
                info_box_draw.text((20, box_y - info_y), f"{key}: {value}", 
                                    font=font, fill=text_color)
                box_y += 35

            # Paste khung thông tin lên ảnh nền
            background.paste(info_box, (info_x, info_y), info_box)

            # Lưu ảnh
            background.save(output_path, quality=95)
            print(f"Ảnh đã được lưu tại: {output_path}")

            # Gửi ảnh
            client.sendLocalImage(
                output_path,
                thread_id,
                thread_type,
                width=1100,
                height=600
            )
            os.remove(output_path)

        except ZaloAPIException as zae:
            print(f"ZaloAPI Error: {zae}")
            client.replyMessage(
                Message(text=f"• Lỗi ZaloAPI: {str(zae)}"), 
                message_object, thread_id, thread_type
            )
        except Exception as e:
            print(f"Lỗi không xác định: {e}")
            client.replyMessage(
                Message(text=f"• Lỗi không xác định: {str(e)}"), 
                message_object, thread_id, thread_type
            )

    except Exception as e:
        print(f"Lỗi chung: {e}")
        client.replyMessage(
            Message(text="• Đã xảy ra lỗi không mong muốn"), 
            message_object, thread_id, thread_type
        )

def get_tmii():
    return {
        'info': in4
    }