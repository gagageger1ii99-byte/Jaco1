import subprocess
import time
import sys
import re
from curl_cffi import requests

JACO_SHARE_URL = "https://l.jaco.live/byOcscLNLM"
RESTREAM_KEY = "re_11725544_event26e01ff7e85c4d7da9516028613ba1dc"
RESTREAM_TARGET = f"rtmp://live.restream.io/live/{RESTREAM_KEY}"

def get_jaco_stream_url(share_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8"
    }
    try:
        # تتبع الرابط القصير لمعرفة الصفحة الأصلية أو معرف الـ Stream
        session = requests.Session()
        resp = session.get(share_url, headers=headers, impersonate="safari_ios", allow_redirects=True)
        final_url = resp.url
        html_content = resp.text
        
        print(f"[*] Resolved URL: {final_url}", flush=True)

        # البحث عن روابط الـ m3u8 أو الرابط المباشر في النصوص أو البيانات المخفية
        match = re.search(r'(https?://[^\s<>"]+?\.(?:m3u8|flv|mp4)[^\s<>"]*)', html_content)
        if match:
            return match.group(1)
            
        # البحث عن روابط بديلة لو كانت بصيغة JSON داخل الصفحة
        match_json = re.search(r'"playbackUrl"\s*:\s*"([^"]+)"', html_content)
        if match_json:
            stream_url = match_json.group(1).replace(r'\/', '/')
            return stream_url
            
    except Exception as e:
        print(f"[-] Error parsing Jaco stream: {e}", flush=True)
        
    return None

def start_bridge():
    print(f"[*] Starting Jaco to Restream Bridge...", flush=True)
    
    while True:
        p2 = None
        try:
            print("[*] Fetching secure Jaco stream direct URL...", flush=True)
            direct_url = get_jaco_stream_url(JACO_SHARE_URL)
            
            if not direct_url:
                print("[!] Stream URL not found or channel is currently offline. Retrying in 15 seconds...", flush=True)
                time.sleep(15)
                continue

            print(f"[*] Secure stream URL acquired: {direct_url[:50]}...", flush=True)
            
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
                    print(f"\n[!] FFmpeg stream ended with code {retcode}. Reconnecting...", flush=True)
                    break
                time.sleep(10)
                
        except Exception as e:
            print(f"[-] Error: {e}", flush=True)
            
        try:
            if p2: p2.kill()
        except:
            pass
            
        print("[!] Re-checking stream status in 5 seconds...", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    start_bridge()
