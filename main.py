import os
import subprocess
import requests

# ----------------- عبي بياناتك هنا مباشرة -----------------
PLATFORM = "youtube"              # المنصة (مثلاً: youtube أو restream)
CHANNEL_NAME = "اسم_قناة_كيك_هنا"   # اكتب اسم قناة كيك هنا بين الأقواس
STREAM_KEY = "مفتاح_البث_هنا"       # الصق مفتاح البث حق يوتيوب هنا بين الأقواس
# -----------------------------------------------------------

print(f"Fetching live stream for Kick channel: {CHANNEL_NAME}...")

kick_api_url = f"https://kick.com/api/v2/channels/{CHANNEL_NAME}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    response = requests.get(kick_api_url, headers=headers)
    data = response.json()
    
    playback_url = data.get("playback_url")
    
    if not playback_url:
        print("Error: The channel is offline or playback URL not found!")
        exit(1)
        
    print(f"Found playback URL: {playback_url}")
except Exception as e:
    print(f"Error fetching Kick API: {e}")
    exit(1)

if PLATFORM == "youtube":
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
elif PLATFORM == "restream":
    rtmp_url = f"rtmp://live.restream.io/live/{STREAM_KEY}"
else:
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"

print(f"Starting bridge to platform: {PLATFORM}")

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
