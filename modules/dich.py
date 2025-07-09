from zlapi import ZaloAPI
from zlapi.models import *
from deep_translator import GoogleTranslator

des = {
    'version': "1.0.0",
    'credits': "LAMDev",
    'description': "Dịch ngôn ngữ"
}

# Danh sách mã ngôn ngữ bạn có thể lấy link bên ngoài, hoặc bạn có thể tự tạo dict tạm nếu muốn

def handle_translate_command(message, message_object, thread_id, thread_type, author_id, client):
    message_text = message_object.get('content', '').strip()

    parts = message_text.split(maxsplit=2)
    if len(parts) < 3:
        client.replyMessage(
            Message(text="Vui lòng nhập ngôn ngữ đích và văn bản cần dịch.\n"
                         "Ví dụ: dich vi Xin chào bạn\n"
                         "Tham khảo mã ngôn ngữ tại: https://cloud.google.com/translate/docs/languages"),
            message_object, thread_id, thread_type, ttl=30000
        )
        return

    target_language = parts[1].lower()
    text_to_translate = parts[2]

    # Kiểm tra mã ngôn ngữ có hợp lệ không (tùy chọn)
    supported_languages = {
        'af', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bm', 'eu', 'be', 'bn', 'bho', 'bs',
        'bg', 'ca', 'ceb', 'ny', 'zh-cn', 'zh-tw', 'co', 'hr', 'cs', 'da', 'dv', 'doi', 'nl',
        'en', 'eo', 'et', 'ee', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gn', 'gu',
        'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'ilo', 'id', 'ga', 'it', 'ja',
        'jw', 'kn', 'kk', 'km', 'rw', 'gom', 'ko', 'kri', 'ku', 'ckb', 'ky', 'lo', 'la', 'lv',
        'ln', 'lt', 'lg', 'lb', 'mk', 'mai', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mni-mtei',
        'lus', 'mn', 'my', 'ne', 'no', 'or', 'om', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro',
        'ru', 'sm', 'sa', 'gd', 'nso', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es',
        'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th', 'ti', 'ts', 'tr', 'tk', 'ak', 'uk',
        'ur', 'ug', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu'
    }

    if target_language not in supported_languages:
        client.replyMessage(
            Message(text=f"Ngôn ngữ '{target_language}' không được hỗ trợ.\n"
                         "Vui lòng chọn mã ngôn ngữ hợp lệ.\n"
                         "Xem danh sách mã tại: https://cloud.google.com/translate/docs/languages"),
            message_object, thread_id, thread_type, ttl=30000
        )
        return

    try:
        translated = GoogleTranslator(source='auto', target=target_language).translate(text_to_translate)
        response = f"Dịch từ '{text_to_translate}' sang '{target_language}':\n{translated}"
        client.replyMessage(Message(text=response), message_object, thread_id, thread_type, ttl=300000)
    except Exception as e:
        client.replyMessage(
            Message(text=f"Lỗi khi dịch: {str(e)}"),
            message_object, thread_id, thread_type, ttl=30000
        )

def get_tmii():
    return {
        'dich': handle_translate_command
    }
