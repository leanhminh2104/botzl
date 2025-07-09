##ok
from zlapi.models import Message
import requests
from bs4 import BeautifulSoup
import os
import re
import time

des = {
    'version': "1.2.0",
    'credits': "LAMDev",
    'description': "Tải nhạc từ SoundCloud"
}

user_states = {}
client_id_cache = None
SEARCH_TIMEOUT = 120

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": 'https://soundcloud.com/',
        "Upgrade-Insecure-Requests": "1"
    }

def get_client_id():
    global client_id_cache
    if client_id_cache:
        return client_id_cache
    try:
        res = requests.get('https://soundcloud.com/', headers=get_headers())
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        script_tags = soup.find_all('script', {'crossorigin': True})
        urls = [tag.get('src') for tag in script_tags if tag.get('src') and tag.get('src').startswith('https')]
        if not urls:
            raise Exception('Không tìm thấy URL script')
        res = requests.get(urls[-1], headers=get_headers())
        res.raise_for_status()
        client_id_cache = re.search(r'client_id:"(.*?)"', res.text).group(1)
        return client_id_cache
    except:
        return None

def wait_for_client_id():
    client_id = get_client_id()
    while not client_id:
        time.sleep(2)
        client_id = get_client_id()
    return client_id

def search_songs(query):
    try:
        base_url = 'https://soundcloud.com'
        search_url = f'https://m.soundcloud.com/search?q={requests.utils.quote(query)}'
        response = requests.get(search_url, headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        songs = []
        url_pattern = re.compile(r'^/[^/]+/[^/]+$')
        for element in soup.select('li > div'):
            a_tag = element.select_one('a')
            if a_tag and a_tag.has_attr('href'):
                relative_url = a_tag['href']
                if url_pattern.match(relative_url):
                    title = a_tag.get('aria-label', '').strip()
                    link = base_url + relative_url
                    img_tag = element.select_one('img')
                    cover_url = img_tag['src'] if (img_tag and img_tag.has_attr('src')) else ""
                    songs.append((link, title, cover_url))
            if len(songs) >= 10:
                break
        return songs
    except:
        return []

def get_music_stream_url(link):
    try:
        client_id = wait_for_client_id()
        api_url = f'https://api-v2.soundcloud.com/resolve?url={link}&client_id={client_id}'
        response = requests.get(api_url, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        for transcode in data.get('media', {}).get('transcodings', []):
            if transcode['format']['protocol'] == 'progressive':
                stream_url = transcode['url']
                stream_response = requests.get(f"{stream_url}?client_id={client_id}", headers=get_headers())
                stream_response.raise_for_status()
                return stream_response.json().get('url')
        return None
    except:
        return None

def get_track_cover(link):
    try:
        client_id = wait_for_client_id()
        api_url = f'https://api-v2.soundcloud.com/resolve?url={link}&client_id={client_id}'
        response = requests.get(api_url, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        cover_url = data.get("artwork_url")
        if cover_url:
            cover_url = cover_url.replace('-large', '-t500x500')
        else:
            cover_url = data.get("user", {}).get("avatar_url", "")
            if cover_url:
                cover_url = cover_url.replace('-large', '-t500x500')
        return cover_url
    except:
        return None

def save_file_to_cache(url, filename):
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        file_path = os.path.join(cache_dir, filename)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    except:
        return None

def upload_to_uguu(file_path):
    try:
        with open(file_path, 'rb') as file:
            response = requests.post("https://uguu.se/upload", files={'files[]': file})
            response.raise_for_status()
            return response.json().get('files')[0].get('url')
    except:
        return None

def delete_file(file_path):
    try:
        os.remove(file_path)
    except:
        pass

def handle_scl_command(message, message_object, thread_id, thread_type, author_id, client):
    global user_states
    content = message.strip().split()
    if len(content) < 2:
        client.replyMessage(
            Message(text="Vui lòng nhập tên bài hát để tìm kiếm."),
            message_object, thread_id, thread_type,
            ttl=60000
        )
        return
    if author_id in user_states:
        state = user_states[author_id]
        time_passed = time.time() - state['time_of_search']
        if time_passed < SEARCH_TIMEOUT:
            if not all(item.isdigit() for item in content[1:]):
                remaining = SEARCH_TIMEOUT - int(time_passed)
                client.replyMessage(
                    Message(text=f"Bạn còn {remaining} giây để chọn bài từ kết quả trước. Hãy chọn số hoặc chờ hết 120s."),
                    message_object, thread_id, thread_type,
                    ttl=30000
                )
                return
        else:
            del user_states[author_id]
    if all(item.isdigit() for item in content[1:]):
        if author_id not in user_states:
            client.replyMessage(
                Message(text="Không có dữ liệu tìm kiếm gần đây hoặc đã hết hạn."),
                message_object, thread_id, thread_type,
                ttl=30000
            )
            return
        state = user_states[author_id]
        time_passed = time.time() - state['time_of_search']
        if time_passed > SEARCH_TIMEOUT:
            del user_states[author_id]
            client.replyMessage(
                Message(text="Kết quả đã hết hạn, vui lòng tìm kiếm lại."),
                message_object, thread_id, thread_type,
                ttl=30000
            )
            return
        songs = state['songs']
        selected_indices = [int(num) - 1 for num in content[1:]]
        some_valid_picked = False
        for index in selected_indices:
            if index < 0 or index >= len(songs):
                client.replyMessage(
                    Message(text=f"Số thứ tự không hợp lệ: {index + 1}"),
                    message_object, thread_id, thread_type,
                    ttl=30000
                )
                continue
            some_valid_picked = True
            link, title, _ = songs[index]
            client.replyMessage(
                Message(text=f"Đang tải xuống: {title}..."),
                message_object, thread_id, thread_type,
                ttl=30000
            )
            cover_main = get_track_cover(link)
            cover_path = None
            if cover_main:
                cover_path = save_file_to_cache(cover_main, f"{title}_cover.jpg")
            audio_url = get_music_stream_url(link)
            if not audio_url:
                client.replyMessage(
                    Message(text=f"Không thể tải: {title}"),
                    message_object, thread_id, thread_type,
                    ttl=30000
                )
                if cover_path:
                    delete_file(cover_path)
                continue
            file_path = save_file_to_cache(audio_url, f"{title}.mp3")
            if not file_path:
                client.replyMessage(
                    Message(text=f"Lỗi lưu tệp: {title}"),
                    message_object, thread_id, thread_type,
                    ttl=30000
                )
                if cover_path:
                    delete_file(cover_path)
                continue
            upload_response = upload_to_uguu(file_path)
            delete_file(file_path)
            if not upload_response:
                client.replyMessage(
                    Message(text=f"Lỗi tải lên: {title}"),
                    message_object, thread_id, thread_type,
                    ttl=30000
                )
                if cover_path:
                    delete_file(cover_path)
                continue
            client.sendRemoteVoice(
                voiceUrl=upload_response,
                thread_id=thread_id,
                thread_type=thread_type,
                ttl=300000
            )
            if cover_path:
                text_to_send = (
                    f" {title} \n\n"
                    f"Link gốc: {link}\n"
                    f"Link voice: {upload_response}\n\n"
                    "— Đây là bìa chính của bài hát —"
                )
                client.sendLocalImage(
                    cover_path,
                    thread_id,
                    thread_type,
                    message=Message(text=text_to_send),
                    ttl=300000
                )
                delete_file(cover_path)
            else:
                client.replyMessage(
                    Message(text=f"{title} đã sẵn sàng!"),
                    message_object, thread_id, thread_type,
                    ttl=30000
                )
        if some_valid_picked:
            del user_states[author_id]
        return
    query = ' '.join(content[1:])
    songs = search_songs(query)
    if not songs:
        client.replyMessage(
            Message(text="Không tìm thấy bài hát."),
            message_object, thread_id, thread_type,
            ttl=30000
        )
        return
    user_states[author_id] = {
        'songs': songs,
        'time_of_search': time.time()
    }
    song_list_text = [f"{i+1}. {s[1]} - Link: {s[0]}" for i, s in enumerate(songs)]
    list_text = "Tìm thấy {} bài hát:\n\n".format(len(songs))
    list_text += "\n".join(song_list_text)
    list_text += "\n\nĐể tải, hãy nhập: scl <số>.\nBạn có 120 giây để chọn."
    first_cover_url = songs[0][2] if songs and songs[0][2] else None
    if first_cover_url:
        cover_path = save_file_to_cache(first_cover_url, "cover_first.jpg")
        if cover_path:
            client.sendLocalImage(
                cover_path,
                thread_id,
                thread_type,
                message=Message(text=list_text),
                ttl=120000
            )
            delete_file(cover_path)
            return
    client.replyMessage(
        Message(text=list_text),
        message_object, thread_id, thread_type,
        ttl=120000
    )


def get_tmii():
    return {
        'nhac': handle_scl_command
    }