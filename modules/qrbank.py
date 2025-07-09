from zlapi.models import Message
import requests

# Thông tin module
des = {
    'version': "1.0.8",
    'credits': "LAMDev",
    'description': "Tạo QRBank từ cú pháp sử dụng dấu phẩy, hỗ trợ bỏ trống giữa chừng và gửi mô tả kèm ảnh"
}

def handle_qrbank_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        if isinstance(message, Message):
            msg_text = message.text
        else:
            msg_text = message

        # Loại bỏ tiền tố lệnh
        if msg_text.startswith("qrbank") or msg_text.startswith("..qrbank"):
            msg_text = msg_text[msg_text.find("qrbank") + len("qrbank"):].strip()

        # Tách bằng dấu phẩy nhưng giữ phần tử rỗng
        parts = msg_text.split(",")

        if len(parts) < 2 or not parts[0].strip() or not parts[1].strip():
            client.sendMessage(
                Message(text="❗ Cú pháp đúng: qrbank <nganhang>,<stk>[,<ctk>,<sotien>,<noidung>]"),
                thread_id, thread_type,
                ttl=3000
            )
            return

        # Lấy các tham số theo vị trí, cho phép để trống
        nganhang = parts[0].strip()
        stk      = parts[1].strip()
        ctk      = parts[2].strip() if len(parts) > 2 else ""
        sotien   = parts[3].strip() if len(parts) > 3 else "0"
        noidung  = parts[4].strip() if len(parts) > 4 else ""

        # Gọi API tạo QR
        api_url  = f"https://api.leanhminh.io.vn/tienich/qrbank/?nganhang={nganhang}&stk={stk}&ctk={ctk}&sotien={sotien}&noidung={noidung}"
        response = requests.get(api_url)
        response.raise_for_status()
        json_data = response.json()

        if json_data.get("success"):
            qr_url = json_data["url"]
            # Soạn nội dung mô tả
            desc = (
                f"💳 QR cho ngân hàng {nganhang.upper()}"
                + (f"\n💳 STK: {stk}")
                + (f"\n👤 Chủ TK: {ctk}" if ctk else "")
                + (f"\n💰 Số tiền: {sotien}đ" if sotien and sotien!="0" else "")
                + (f"\n📝 Nội dung: {noidung}" if noidung else "")
            )
            # Gửi ảnh QR kèm mô tả trong cùng một tin nhắn
            client.sendImage(
                qr_url,
                thread_id=thread_id,
                thread_type=thread_type,
                width=1200,
                height=1600,
                message=Message(text=desc),
                ttl=3000000
            )
        else:
            client.sendMessage(
                Message(text=f"❌ Lỗi tạo QR: {json_data.get('error', 'Không rõ lỗi')}"),
                thread_id, thread_type,
                ttl=3000
            )

    except requests.exceptions.RequestException as e:
        client.sendMessage(
            Message(text=f"🌐 Lỗi khi gọi API: {str(e)}"),
            thread_id, thread_type,
            ttl=3000
        )
    except Exception as e:
        client.sendMessage(
            Message(text=f"⚠️ Lỗi hệ thống: {str(e)}"),
            thread_id, thread_type,
            ttl=3000
        )

def get_tmii():
    return {
        'qrbank': handle_qrbank_command
    }
