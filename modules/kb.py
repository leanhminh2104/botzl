from zlapi.models import Message
import time

ADMIN_ID = "3704058103894860815"  # ID admin
DELAY_SEND = 1  # Giây nghỉ giữa mỗi lời mời

des = {
    'version': "1.0.1",
    'credits': "LAMDev",
    'description': "Gửi lời mời kết bạn đến tất cả thành viên trong nhóm"
}

def is_admin(author_id):
    return author_id == ADMIN_ID

def handle_add_group_command(message, message_object, thread_id, thread_type, author_id, client):
    if not is_admin(author_id):
        client.replyMessage(
            Message(text="❌ Chỉ admin mới được dùng lệnh này."),
            message_object, thread_id, thread_type, ttl=3000
        )
        return

    try:
        group_info_data = client.fetchGroupInfo(thread_id)
        group_info_map = getattr(group_info_data, 'gridInfoMap', {})

        if thread_id not in group_info_map:
            client.replyMessage(
                Message(text="❌ Không lấy được thông tin nhóm."),
                message_object, thread_id, thread_type, ttl=3000
            )
            return

        group_info = group_info_map[thread_id]
        members = group_info.get('memVerList', [])

        if not members:
            client.replyMessage(
                Message(text="⚠️ Nhóm không có thành viên hoặc không lấy được danh sách thành viên."),
                message_object, thread_id, thread_type, ttl=3000
            )
            return

        total_members = len(members)
        successful_requests = 0
        failed_requests = []

        client.replyMessage(
            Message(text=f"🔄 Bắt đầu gửi lời mời đến {total_members} thành viên..."),
            message_object, thread_id, thread_type, ttl=10000
        )

        for mem in members:
            try:
                user_id, user_name = mem.split('_')
            except ValueError:
                continue

            if user_id == ADMIN_ID:
                continue

            try:
                client.sendFriendRequest(
                    userId=user_id,
                    msg=f"🤖 Xin chào {user_name}, tôi là bot, hãy chấp nhận lời mời kết bạn nhé!"
                )
                successful_requests += 1
            except Exception as e:
                failed_requests.append((user_name, str(e)))

            time.sleep(DELAY_SEND)

        msg = (
            f"✅ Đã gửi lời mời kết bạn đến các thành viên trong nhóm.\n"
            f"👥 Tổng: {total_members}\n"
            f"📬 Thành công: {successful_requests}\n"
            f"❌ Thất bại: {len(failed_requests)}"
        )

        if failed_requests:
            msg += "\n\nMột số lỗi:\n" + "\n".join([f"{u}: {err}" for u, err in failed_requests[:5]])

        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=30000)

    except Exception as e:
        client.replyMessage(
            Message(text=f"❌ Lỗi trong quá trình xử lý: {str(e)}"),
            message_object, thread_id, thread_type, ttl=5000
        )

def get_tmii():
    return {
        'kb': handle_add_group_command
    }
