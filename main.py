import subprocess
import time
import sys
import re
from curl_cffi import requests

# الرابط المباشر للغرفة بعد التحويل
JACO_ROOM_URL = "https://jaco.live/@3scc?lang=ar&lid=5326743192420544&theme=dark&uid=3007200367"
RESTREAM_KEY = "re_11725544_event26e01ff7e85c4d7da9516028613ba1dc"
RESTREAM_TARGET = f"rtmp://live.restream.io/live/{RESTREAM_KEY}"

def get_jaco_stream_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://jaco.live/"
    }
    try:
        response = requests.get(url, headers=headers, impersonate="safari_ios")
        if response.status_code == 200:
            html_content = response.text
            
            # البحث عن أي نمط لـ m3u8 أو flv داخل بيانات السكربت المخفية في الصفحة
            matches = re.findall(r'"(https?://[^"]+?\.(?:m3u8|flv|mp4)[^"]*)"', html_content)
            for m in matches:
                clean_url = m.replace(r'\/', '/')
                if "m3u8" in clean_url or "flv" in clean_url:
                    print(f"[*] Found stream target: {clean_url}", flush=True)
                    return clean_url
                    
    except Exception as e:
        print(f"[-] Error: {e}", flush=True)
    return None

def start_bridge():
    print(f"[*] Starting Jaco Bridge for room...", flush=True)
    
    while True:
        p2 = None
        try:
            direct_url = get_jaco_stream_url(JACO_ROOM_URL)
            
            if not direct_url:
                print("[!] Stream URL not found or waiting for broadcast. Retrying in 15 seconds...", flush=True)
                time.sleep(15)
                continue

            print(f"[*] Launching FFmpeg...", flush=True)
            
            ffmpeg_cmd = [
                "ffmpeg",
                "-re",
                "-fflags", "+genpts+nobuffer",
                "-user_agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
                "-i", direct_url,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-maxrate", "3000k",
                "-bufsize", "6000k",
                "-pix_fmt", "yuv420p",
                "-g", "60",
                "-c:a", "aac",
                "-b:a", "128k",
                "-ar", "44100",
                "-f", "flv",
                RESTREAM_TARGET
            ]
            
            p2 = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            while True:
                retcode = p2.poll()
                if retcode is not None:
                    print(f"\n[!] FFmpeg ended with code {retcode}. Reconnecting...", flush=True)
                    break
                time.sleep(10)
                
        except Exception as e:
            print(f"[-] Error: {e}", flush=True)
            
        try:
            if p2: p2.kill()
        except:
            pass
            
        print("[!] Re-checking in 5 seconds...", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    start_bridge()
