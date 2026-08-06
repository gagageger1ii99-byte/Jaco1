import os
import subprocess

channel_name = os.getenv("CHANNEL_NAME")
stream_key = os.getenv("STREAM_KEY")

print(f"Starting stream for channel: {channel_name}")

# رابط يوتيوب RTMP الأساسي مدمجاً معه مفتاح البث
rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

# هنا رابط مصدر الفيديو أو البث (مثلاً رابط قناة تليجرام، فيديو، أو مصدر آخر)
# ضع رابط البث أو الفيديو الذي تريد إعادة توجيهه
input_source = f"https://t.me/{channel_name}" # أو استبدله برابط الفيديو المباشر

# أمر FFmpeg لإرسال البث إلى يوتيوب
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

# تنفيذ الأمر وبدء البث الفعلي
subprocess.run(cmd)
