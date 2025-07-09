import asyncio
import time
from zlapi.models import Message, ThreadType
from config import *

# Module metadata
des = {
    'version': "1.3.1",
    'credits': "DuongNgocc",
    'description': "Gửi spam công việc nhanh hơn với asyncio semaphore và báo cáo kết quả cùng thời gian chạy."
}

async def check_group_access(thread_id, sender_id):
    if thread_id in ALLOW_GR and sender_id not in ADMIN:
        return False
    return True  
    print(f"Bot đang trả lời trong nhóm {thread_id} từ người {sender_id}")
async def send_task(client, message_object, content, tagged_user):
    """
    Hàm không đồng bộ để gửi một công việc.
    """
    await client.sendToDo(
        message_object=message_object,
        content=content,
        assignees=[tagged_user],
        thread_id=tagged_user,
        thread_type=ThreadType.USER,
        due_date=-1,
        description="huang"
    )

async def limited_send_task(semaphore, client, message_object, content, tagged_user):
    """
    Gửi công việc với giới hạn đồng thời.
    """
    async with semaphore:
        return await send_task(client, message_object, content, tagged_user)

async def handle_spamtodo_command_async(client, message_object, thread_id, thread_type, author_id, message):
    """
    Hàm chính để xử lý lệnh spamtodo không đồng bộ.
    """
    if not check_group_access(thread_id, author_id):
        return
    if author_id not in ADMIN:
        await client.replyMessage(
            Message(text="Bạn không có quyền thực hiện lệnh này."),
            message_object, thread_id, thread_type
        )
        return

    # Phân tích cú pháp lệnh
    parts = message.split(' ', 3)
    if len(parts) < 4:
        response_message = (
            "Vui lòng cung cấp UID, nội dung và số lần spam công việc. "
            "Ví dụ: spamtodo <uid> <nội dung> <số lần>"
        )
        await client.replyMessage(Message(text=response_message), message_object, thread_id, thread_type)
        return

    tagged_user, content = parts[1], parts[2]
    try:
        num_repeats = int(parts[3])
    except ValueError:
        response_message = "Số lần phải là một số nguyên."
        await client.replyMessage(Message(text=response_message), message_object, thread_id, thread_type)
        return

    if num_repeats > 0:
        client.replyMessage(Message(text="Đang tiến hành spam..."), message_object, thread_id, thread_type)

        # Bắt đầu đếm thời gian
        start_time = time.perf_counter()

        # Sử dụng semaphore để giới hạn số tác vụ đồng thời
        max_concurrent_tasks = 100  # Điều chỉnh số lượng phù hợp với hệ thống
        semaphore = asyncio.Semaphore(max_concurrent_tasks)

        tasks = [limited_send_task(semaphore, client, message_object, content, tagged_user) for _ in range(num_repeats)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Dừng đếm thời gian
        end_time = time.perf_counter()

        # Đếm số lần thành công và thất bại
        success_count = sum(1 for result in results if result is True)
        failure_count = num_repeats - success_count

        # Tính thời gian chạy
        elapsed_time = end_time - start_time

        # Gửi thông báo kết quả
        result_message = (
            f"Hoàn thành spam {num_repeats} công việc.\n"
            f"- Thời gian chạy: {elapsed_time:.2f} giây."
        )
        await client.replyMessage(Message(text=result_message), message_object, thread_id, thread_type)
    else:
        await client.replyMessage(Message(text="Số lần spam phải lớn hơn 0."), message_object, thread_id, thread_type)

def handle_spamtodo_command(message, message_object, thread_id, thread_type, author_id, client):
    """
    Gọi hàm asyncio cho spamtodo.
    """
    asyncio.run(handle_spamtodo_command_async(client, message_object, thread_id, thread_type, author_id, message))

def get_tmii():
    return {
        'spamtodo': handle_spamtodo_command
    }
