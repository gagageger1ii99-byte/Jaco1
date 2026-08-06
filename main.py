import subprocess
import time
import sys

JACO_URL = "https://l.jaco.live/byOcscLNLM"
RESTREAM_KEY = "re_11725544_event26e01ff7e85c4d7da9516028613ba1dc"
RESTREAM_TARGET = f"rtmp://live.restream.io/live/{RESTREAM_KEY}"

def start_bridge():
    print(f"[*] Starting Jaco to Restream Bridge for: {JACO_URL}", flush=True)
    
    ytdlp_cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-check-certificates",
        "--geo-bypass",
        "--extractor-args", "generic:impersonate=chrome",
        "--get-url",
        JACO_URL
    ]
    
    while True:
        p2 = None
        try:
            print("[*] Fetching secure Jaco stream direct URL...", flush=True)
            direct_url = subprocess.check_output(ytdlp_cmd, universal_newlines=True).strip()
            
            if not direct_url or "http" not in direct_url:
                print("[!] Stream URL not found or channel is currently offline. Retrying in 15 seconds...", flush=True)
                time.sleep(15)
                continue

            print("[*] Secure stream URL acquired! Launching FFmpeg to Restream...", flush=True)
            
            ffmpeg_cmd = [
                "ffmpeg",
                "-re",
                "-fflags", "+genpts+nobuffer",
                "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
            print(f"\n[-] Error: {e}", flush=True)
            
        try:
            if p2: p2.kill()
        except:
            pass
            
        print("[!] Re-checking stream status in 5 seconds...", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    start_bridge()

