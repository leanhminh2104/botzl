import os
from zlapi import ZaloAPI
from zlapi.models import *
import importlib

des = {
    'version': "1.0.2",
    'credits': "LAMDev",
    'description': "Lệnh này cung cấp thông tin chi tiết về các lệnh khác."
}

def get_all_tmii():
    tmii = {}

    for module_name in os.listdir('modules'):
        if module_name.endswith('.py') and module_name != '__init__.py':
            module_path = f'modules.{module_name[:-3]}'
            module = importlib.import_module(module_path)

            if hasattr(module, 'get_tmii'):
                module_tmii = module.get_tmii()
                tmii.update(module_tmii)

    command_names = list(tmii.keys())
    
    return command_names

def handle_menu_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        command_names = get_all_tmii()
        total_tmii = len(command_names)
        numbered_tmii = "\n".join([f"│{i + 1}. {name}" for i, name in enumerate(command_names)])
        menu_message = (
            f"╭────────────────────────────╮\n"
            f"│ Bot LAMDev - SIEUTHIMMO\n"
            f"│ Tổng Số Lệnh: {total_tmii}\n"
            f"├────────────────────────────╯\n"
            f"├────────────────────────────╮\n"
            f"{numbered_tmii}\n"
            f"╰────────────────────────────╯"
        )
        style = MultiMsgStyle([
            MessageStyle(offset=0, length=len(menu_message), style="font", size="12", auto_format=False),
            MessageStyle(offset=0, length=len(menu_message), style="bold", auto_format=False)
        ])
        styled_message = Message(text=menu_message, style=style)
        client.replyMessage(styled_message, message_object, thread_id, thread_type, ttl=300000)
    except Exception as e:
        print(f"Lỗi khi gửi menu với style: {e}")
def get_tmii():
    return {
        '.': handle_menu_command
    }