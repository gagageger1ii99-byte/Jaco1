import os
import subprocess
import requests
import threading

def start_stream(index, channel_name, stream_key, platform):
    if not channel_name or not stream_key:
        print(f"[Stream {index}] Skipped: Channel name or Stream key is empty.")
        return

    platform = platform.lower()
    print(f"[Stream {index}] Fetching live stream for Kick channel: {channel_name}...")

    kick_api_url = f"https://kick.com/api/v2/channels/{channel_name}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        response = requests.get(kick_api_url, headers=headers)
        data = response.json()
        playback_url = data.get("playback_url")
        
        if not playback_url:
            print(f"[Stream {index}] Error: Channel {channel_name} is offline or URL not found!")
            return
            
        print(f"[Stream {index}] Found playback URL: {playback_url}")
    except Exception as e:
        print(f"[Stream {index}] Error fetching Kick API: {e}")
        return

    if platform == "restream":
        rtmp_url = f"rtmp://live.restream.io/live/{stream_key}"
    else:
        rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

    print(f"[Stream {index}] Starting bridge to {platform}...")

    cmd = [
        "ffmpeg",
        "-re",
        "-i", playback_url,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-maxrate", "4500k",
        "-bufsize", "9000k",
        "-pix_fmt", "yuv420p",
        "-g", "60",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        rtmp_url
    ]

    subprocess.run(cmd)

streams = [
    (1, os.getenv("CHANNEL_1"), os.getenv("KEY_1"), os.getenv("PLATFORM_1", "youtube")),
    (2, os.getenv("CHANNEL_2"), os.getenv("KEY_2"), os.getenv("PLATFORM_2", "youtube")),
    (3, os.getenv("CHANNEL_3"), os.getenv("KEY_3"), os.getenv("PLATFORM_3", "youtube")),
]

threads = []
for idx, ch, key, plat in streams:
    if ch and key:
        t = threading.Thread(target=start_stream, args=(idx, ch, key, plat))
        threads.append(t)
        t.start()

for t in threads:
    t.join()

print("All stream processes finished.")
