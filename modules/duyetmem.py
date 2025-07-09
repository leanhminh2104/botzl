from zlapi.models import Message
from config import *
import time

des = {
    'version': "1.0.1",
    'credits': "DuongNgocc",
    'description': "Duyệt tất cả thành viên"
}

def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
def handle_duyetmem_command(message, message_object, thread_id, thread_type, author_id, client):
    if not check_group_access(thread_id, author_id):
        return
    try:
        group_info = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]
        creator_id = group_info.get('creatorId')
        admin_ids = group_info.get('adminIds', [])

        if admin_ids is None:
            admin_ids = []

        all_admin_ids = set(admin_ids)
        all_admin_ids.add(creator_id)
        all_admin_ids.update(ADMIN)

        if author_id not in all_admin_ids and author_id not in ADMIN:
            client.replyMessage(
                Message(text="Bạn không có quyền sử dụng lệnh này."),
                message_object, thread_id, thread_type
            )
            return

        pending_members = group_info.pendingApprove.get('uids', [])

        command_parts = message.strip().split()

        if len(command_parts) < 2:
            client.replyMessage(
                Message(text="Lệnh không hợp lệ. Vui lòng sử dụng `duyetmem list` để xem danh sách hoặc `duyetmem all` để duyệt tất cả."),
                message_object, thread_id, thread_type
            )
            return

        action = command_parts[1]

        if action == "list":
            if not pending_members:
                client.replyMessage(
                    Message(text="Hiện tại không có thành viên nào đang chờ duyệt."),
                    message_object, thread_id, thread_type
                )
            else:
                client.replyMessage(
                    Message(text=f"Số thành viên đang chờ duyệt: {len(pending_members)} thành viên"),
                    message_object, thread_id, thread_type
                )
        elif action == "all":
            if not pending_members:
                client.replyMessage(
                    Message(text="Hiện tại không có thành viên nào đang chờ duyệt."),
                    message_object, thread_id, thread_type
                )
                return

            for member_id in pending_members:
                if hasattr(client, 'handleGroupPending'):
                    client.handleGroupPending(member_id, thread_id)
                else:
                    break
                time.sleep(1)

            client.replyMessage(Message(text="Đã hoàn tất duyệt tất cả thành viên."), message_object, thread_id, thread_type)
        else:
            client.replyMessage(
                Message(text="Lệnh không hợp lệ. Vui lòng sử dụng `duyetmem list` để xem danh sách hoặc `duyetmem all` để duyệt tất cả."),
                message_object, thread_id, thread_type
            )

    except Exception as e:
        print(f"Lỗi: {e}")
        client.replyMessage(Message(text=f"Đã xảy ra lỗi khi duyệt.\n{e}"), message_object, thread_id, thread_type)

def get_tmii():
    return {
        'duyetmem': handle_duyetmem_command
    }
