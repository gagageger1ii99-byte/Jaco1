import subprocess
import time
import sys
from curl_cffi import requests

CHANNEL_NAME = "w1pey"
# تم دمج رابط يوتيوب ومفتاح البث الخاص بك هنا مباشرة
YOUTUBE_TARGET = "rtmp://a.rtmp.youtube.com/live2/7swd-bmce-ym7w-5e2m-499u"

def get_kick_playback_url(channel):
    api_url = f"https://kick.com/api/v2/channels/{channel}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://kick.com/",
        "Origin": "https://kick.com/"
    }
    try:
        response = requests.get(api_url, headers=headers, impersonate="chrome")
        if response.status_code == 200:
            data = response.json()
            return data.get('playback_url')
    except Exception as e:
        print(f"[-] Error fetching Kick API: {e}", flush=True)
    return None

def start_bridge():
    print(f"[*] Starting Kick to YouTube Bridge for channel: {CHANNEL_NAME}", flush=True)
    
    while True:
        p2 = None
        try:
            print("[*] Fetching Kick playback URL...", flush=True)
            direct_url = get_kick_playback_url(CHANNEL_NAME)
            
            if not direct_url:
                print("[!] Channel is offline or URL not found. Retrying in 20 seconds...", flush=True)
                time.sleep(20)
                continue

            print(f"[*] Playback URL acquired! Launching FFmpeg to YouTube...", flush=True)
            
            ffmpeg_cmd = [
                "ffmpeg",
                "-re",
                "-fflags", "+genpts+nobuffer",
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
                YOUTUBE_TARGET
            ]
            
            p2 = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # مراقبة حالة البث واستمرار العمل طالما القناة مبثة
            while True:
                retcode = p2.poll()
                if retcode is not None:
                    print(f"\n[!] FFmpeg ended with code {retcode}. Reconnecting...", flush=True)
                    break
                time.sleep(15)
                
        except Exception as e:
            print(f"[-] Error: {e}", flush=True)
            
        try:
            if p2: p2.kill()
        except:
            pass
            
        print("[!] Re-checking channel status in 10 seconds...", flush=True)
        time.sleep(10)

if __name__ == "__main__":
    start_bridge()
