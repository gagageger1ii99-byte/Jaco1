import os
import subprocess

platform = os.getenv("PLATFORM", "youtube").lower()
channel_name = os.getenv("CHANNEL_NAME")
stream_key = os.getenv("STREAM_KEY")

print(f"Starting stream for platform: {platform}, channel: {channel_name}")

# تحديد رابط الـ RTMP بناءً على المنصة المتاحة
if platform == "youtube":
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
elif platform == "restream":
    # رابط ريستريم المباشر مع مفتاح البث الخاص به
    rtmp_url = f"rtmp://live.restream.io/live/{stream_key}"
else:
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

input_source = f"https://t.me/{channel_name}"

cmd = [
    "ffmpeg",
    "-re",
    "-i", input_source,
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
    rtmp_url
]

subprocess.run(cmd)
