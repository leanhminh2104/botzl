from zlapi import ZaloAPI
from zlapi.models import *
import requests
from config import *

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "Gửi video ngẫu nhiên từ API + menu chia trang"
}

MENU_TITLES = {
    0: "LAMDev",
    1: "Ảnh, video",
    2: "Ảnh, Video, Meme",
    3: "Tiện ích",
    4: "Check thông tin",
    5: "Admin"
}

MENU_PAGES = {
    0: [
        "LAMDev", "Lê Anh Minh", "dichvusale.io.vn", 
        "smm.dichvusale.io.vn", "pre.leanhminh.io.vn"
    ],
    1: [
        "1. anhmong", "2. anhgaisexy", "3. anhcosplay", "4. anhdu", "5. anhlkl",
        "6. anh6mui", "7. anhtrai", "8. anhwibu", "9. anhanime", "10. anhgai",
        "11. cosplaytele", "12. vdgai", "13. vdcos", "14. vdchill", "anhnude"
    ],
    2: [
        "1. dich", "2. stk", "3. scanqr", "4. cap2", "5. voice",
        "6. media", "7. nhacrm", "8. nhac", "9. thinh", "10. adc",
        "11. meme", "12. lamnet", "13. lamnetv2", "14. lamnetv3"
    ],
    3: [
        "1. qrcode", "2. menu", "3. imgur", "4. reo", "5. getlink", "6. gay",
        "7. spamtodo", "8. mute", "9. timg", "10. api", "11. cap",
        "12. chill", "13. poll", "14. help"
    ],
    4: [
        "1. cmd", "2. downtik", "3. dowtt", "4. gemini", "5. qrbank",
        "6. in4", "7. info", "8. cardinfo", "9. kick", "10. les",
        "11. infofb", "12. infott", "in4gr"
    ],
    5: [
        "1. reonamegr", "2. keyword", "3. sim", "4. delall", "5. tagan",
        "6. group", "7. thoitiet37", "8. spgr", "9. spgrstop", "10. tagall",
        "11. text", "12. unmute", "13. joker", "14. autosend", "15. quanly",
        "16. thoitiet", "17. addid", "18. add", "19. addkick", "20. del",
        "21. rs", "22. addsdt", "23. duyetmem", "kb"
    ]
}

def check_group_access(thread_id, sender_id):
    return thread_id not in ALLOW_GR

def handle_menu_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return

    try:
        try:
            page = int(message.split(" ")[1]) if len(message.split()) > 1 else 0
        except ValueError:
            page = 0

        if page not in MENU_PAGES:
            raise ValueError("Trang không tồn tại. Vui lòng nhập số từ 0 đến 5.")

        title = MENU_TITLES.get(page, f"Trang {page}")
        menu_lines = MENU_PAGES[page]

        content = (
            f"╭──[ MENU: {title} ]\n"
            f"├────[ TRANG {page}/5 ]────╮\n" +
            "\n".join(f"│ {line}" for line in menu_lines) +
            "\n╰──────────────╯"
        )

        client.send(
            Message(text=content),
            thread_id=thread_id,
            thread_type=thread_type,
            ttl=60000
        )

    except Exception as e:
        client.send(
            Message(text=f"Đã xảy ra lỗi: {str(e)}"),
            thread_id=thread_id,
            thread_type=thread_type,
            ttl=30000
        )

def get_tmii():
    return {
        'admin': handle_menu_command
    }
