import os
import subprocess
import requests

platform = os.getenv("PLATFORM", "youtube").lower()
channel_name = os.getenv("CHANNEL_NAME")
stream_key = os.getenv("STREAM_KEY")

if not channel_name or not stream_key:
    print("Error: CHANNEL_NAME or STREAM_KEY is missing!")
    exit(1)

print(f"Fetching live stream for Kick channel: {channel_name}...")

kick_api_url = f"https://kick.com/api/v2/channels/{channel_name}"
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

if platform == "restream":
    rtmp_url = f"rtmp://live.restream.io/live/{stream_key}"
else:
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

print(f"Starting bridge to platform: {platform}")

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
