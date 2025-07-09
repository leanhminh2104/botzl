import os
import importlib
import sys
import random
import json
from zlapi.models import Message
from config import PREFIX, ADMIN
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules/auto'))
class CommandHandler:
    def __init__(self, client):
        self.client = client
        self.tmii = self.load_tmii()
        self.auto_tmii = self.load_auto_tmii()
        self.admin_id = ADMIN
        self.adminon = self.load_admin_mode()
        self.noprefix_tmii = self.load_noprefix_tmii()
        
        if PREFIX == '':
            print("Prefix hiện tại của bot là 'no prefix'")
        else:
            print(f"Prefix hiện tại của bot là '{PREFIX}'")

    def load_admin_mode(self):
        try:
            with open('modules/cacheadmindata.json', 'r') as f:
                data = json.load(f)
                return data.get('adminon', False)
        except FileNotFoundError:
            return False
        except json.JSONDecodeError:
            return False

    def save_admin_mode(self):
        with open('modules/cache/admindata.json', 'w') as f:
            json.dump({'adminon': self.adminon}, f)

    def load_tmii(self):
        tmii = {}
        modules_path = 'modules'
        success_count = 0
        failed_count = 0
        success_tmii = []
        failed_tmii = []

        for filename in os.listdir(modules_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{modules_path}.{module_name}')
                    
                    if hasattr(module, 'get_tmii'):
                        if hasattr(module, 'des'):
                            des = getattr(module, 'des')
                            if all(key in des for key in ['version', 'credits', 'description']):
                                tmii.update(module.get_tmii())
                                success_count += 1
                                success_tmii.append(module_name)
                            else:
                                raise ImportError(f"Lỗi không thể tìm thấy thông tin của lệnh: {module_name}")
                        else:
                            raise ImportError(f"Lệnh {module_name} không có thông tin")
                    else:
                        raise ImportError(f"Module {module_name} không có hàm gọi lệnh")
                except Exception as e:
                    print(f"Không thể load được module: {module_name}. Lỗi: {e}")
                    failed_count += 1
                    failed_tmii.append(module_name)

        if success_count > 0:
            print(f"Đã load thành công {success_count} lệnh: {', '.join(success_tmii)}")
        if failed_count > 0:
            print(f"Không thể load được {failed_count} lệnh: {', '.join(failed_tmii)}")

        return tmii

    def load_noprefix_tmii(self):
        noprefix_tmii = {}
        noprefix_modules_path = 'modules.noprefix'
        success_count = 0
        failed_count = 0
        success_noprefix_tmii = []
        failed_noprefix_tmii = []

        for filename in os.listdir('modules/noprefix'):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{noprefix_modules_path}.{module_name}')
                    
                    if hasattr(module, 'get_tmii'):
                        if hasattr(module, 'des'):
                            des = getattr(module, 'des')
                            if all(key in des for key in ['version', 'credits', 'description']):
                                noprefix_tmii.update(module.get_tmii())
                                success_count += 1
                                success_noprefix_tmii.append(module_name)
                            else:
                                raise ImportError(f"Module {module_name} thiếu các thông tin cần thiết")
                        else:
                            raise ImportError(f"Lệnh {module_name} không có thông tin")
                    else:
                        raise ImportError(f"Module {module_name} không có hàm gọi lệnh")
                except Exception as e:
                    print(f"Không thể load được module: {module_name}. Lỗi: {e}")
                    failed_count += 1
                    failed_noprefix_tmii.append(module_name)

        if success_count > 0:
            print(f"Đã load thành công {success_count} lệnh noprefix")
        if failed_count > 0:
            print(f"Không thể load được {failed_count} lệnh noprefix: {', '.join(failed_noprefix_tmii)}")

        return noprefix_tmii

    def load_auto_tmii(self):
        autotmii = {}
        auto_modules_path = 'modules/auto'
        success_count = 0
        failed_count = 0
        success_autotmii = []
        failed_autotmii = []

        for filename in os.listdir(auto_modules_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'modules.auto.{module_name}')
                    
                    if hasattr(module, 'start_auto'):
                        autotmii[module_name] = module
                        success_count += 1
                        success_autotmii.append(module_name)
                    else:
                        raise ImportError(f"Module {module_name} không có hàm start_auto")
                except Exception as e:
                    failed_count += 1
                    failed_autotmii.append(module_name)

        if success_count > 0:
            print(f"Đã load thành công {success_count} lệnh auto")
            for module in success_autotmii:
                threading.Thread(target=autotmii[module].start_auto, args=(self.client,)).start()
        if failed_count > 0:
            print(f"Không thể load {failed_count} lệnh auto: {', '.join(failed_autotmii)}")

        return autotmii

    def handle_command(self, message, author_id, message_object, thread_id, thread_type):
        
        auto_command_handler = self.auto_tmii.get(message.lower())
        if auto_command_handler:
            auto_command_handler(message, message_object, thread_id, thread_type, author_id, self.client)
            return

        noprefix_command_handler = self.noprefix_tmii.get(message.lower())
        if noprefix_command_handler:
            noprefix_command_handler(message, message_object, thread_id, thread_type, author_id, self.client)
            return

        if not message.startswith(PREFIX):
            return

        command_name = message[len(PREFIX):].split(' ')[0].lower()
        
        
        command_handler = self.tmii.get(command_name)

        if command_handler:
            command_handler(message, message_object, thread_id, thread_type, author_id, self.client)
        else:
            error_message = f"Không tìm thấy lệnh '{command_name}'. Hãy dùng {PREFIX}menu để biết các lệnh có trên hệ thống."
            self.replyMessage(error_message, message_object, thread_id, thread_type)

    def replyMessage(self, message, message_object, thread_id, thread_type):
        mes = Message(text=message)
        self.client.replyMessage(mes, message_object, thread_id=thread_id, thread_type=thread_type,ttl=60000)
