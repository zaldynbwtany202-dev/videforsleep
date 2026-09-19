import os, subprocess, numpy as np
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

ASSETS_DIR = "/home/user/videforsleep/assets_v3"
AUDIO_DIR = "/home/user/videforsleep/audio_v4_en"
OUT_DIR = "/home/user/videforsleep/output"
os.makedirs(OUT_DIR, exist_ok=True)

scenes = [
    {"image": f"{ASSETS_DIR}/v3_01_station.png", "audio": f"{AUDIO_DIR}/v4_01_station.mp3"},
    {"image": f"{ASSETS_DIR}/v3_02_journal.png", "audio": f"{AUDIO_DIR}/v4_02_journal.mp3"},
    {"image": f"{ASSETS_DIR}/v3_03_lake.png", "audio": f"{AUDIO_DIR}/v4_03_lake.mp3"},
    {"image": f"{ASSETS_DIR}/v3_04_library.png", "audio": f"{AUDIO_DIR}/v4_04_library.mp3"},
    {"image": f"{ASSETS_DIR}/v3_05_cliff.png", "audio": f"{AUDIO_DIR}/v4_05_cliff.mp3"},
]

try:
    from moviepy.editor import AudioFileClip
except:
    from moviepy.audio.io.AudioFileClip import AudioFileClip

audio_clips = [AudioFileClip(s["audio"]) for s in scenes]
total_duration = sum([c.duration for c in audio_clips])
print(f"V4 Morgan Freeman total: {total_duration:.2f}s")

# Ambient - 4 layers, even more cinematic for Morgan Freeman
sample_rate = 44100
duration = total_duration + 8
np.random.seed(777)
white = np.random.randn(int(duration * sample_rate))
brown = np.cumsum(white)
brown = brown - np.mean(brown)
brown = brown / np.max(np.abs(brown)) * 0.07

t = np.arange(len(brown)) / sample_rate
lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.01 * t)
sub = 0.05 * np.sin(2*np.pi*28*t) * lfo + 0.03 * np.sin(2*np.pi*42*t) * lfo
wind = 0.02 * np.random.randn(len(t))
window = int(sample_rate * 0.2)
wind = np.convolve(wind, np.ones(window)/window, mode='same') * (0.3 + 0.7 * np.sin(2*np.pi*0.006*t))
crickets = 0.015 * np.sin(2*np.pi*3800*t) * (0.5 + 0.5 * np.sin(2*np.pi*0.25*t)) * (np.random.rand(len(t)) > 0.75)

ambient = brown * 0.5 + sub + wind * 0.5 + crickets * 0.3
fade = int(8 * sample_rate)
ambient[:fade] *= np.linspace(0,1,fade)
ambient[-fade:] *= np.linspace(1,0,fade)
ambient = ambient / np.max(np.abs(ambient)) * 0.25

ambient_path = f"{OUT_DIR}/ambient_v4_morgan.wav"
import wave
with wave.open(ambient_path, 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes((ambient * 32767).astype(np.int16).tobytes())

# Process narration - Morgan Freeman style: deep, wise, warm, natural, not robotic
processed = []
for i, s in enumerate(scenes):
    src = s["audio"]
    dst = f"{OUT_DIR}/v4_morgan_{i:02d}.wav"
    processed.append(dst)
    # Morgan Freeman processing: very natural, keep human imperfections
    # pitch 0.98 almost natural, tempo 0.94 deliberate wise, warm EQ
    filt = "rubberband=pitch=0.98:tempo=0.94,equalizer=f=180:t=h:width=120:g=2.5,equalizer=f=3000:t=h:width=800:g=-1,lowpass=f=6000,acompressor=threshold=-18dB:ratio=1.5:attack=80:release=500,aecho=0.5:0.7:22:0.05"
    cmd = [FFMPEG, "-y", "-i", src, "-filter:a", filt, "-ar", "44100", dst]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print(f"Processed Morgan {i}")

# Build segments with cinematic
segs = []
for i, s in enumerate(scenes):
    img = s["image"]
    aud = processed[i]
    out = f"{OUT_DIR}/v4_morgan_seg_{i:02d}.mp4"
    segs.append(out)
    dur = AudioFileClip(aud).duration
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p,eq=brightness=-0.04:contrast=1.1:saturation=0.8,vignette=angle=PI/4,noise=c0s=5:c0f=t+u"
    cmd = [FFMPEG, "-y", "-loop", "1", "-framerate", "24", "-i", img, "-i", aud, "-c:v", "libx264", "-t", str(dur), "-vf", vf, "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p", "-shortest", out]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Segment {i} {dur:.2f}s")

# Xfade concat
current = segs[0]
temps = []
for i in range(1, len(segs)):
    nxt = segs[i]
    # Get current duration via AudioFileClip of processed
    # For simplicity, use sum
    # We'll use ffprobe via moviepy? Use approximate
    # Use 1.5s xfade
    dur_prev = AudioFileClip(processed[i-1]).duration
    # For accumulated, we need actual duration of current video file
    # We'll approximate by using total so far
    # Better: use ffprobe
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        dur_cur = VideoFileClip(current).duration
    except:
        dur_cur = dur_prev + 10  # fallback
    xdur = 1.2
    out = f"{OUT_DIR}/v4_xfade_{i}.mp4"
    temps.append(out)
    cmd = [FFMPEG, "-y", "-i", current, "-i", nxt, "-filter_complex", f"[0:v][1:v]xfade=transition=fade:duration={xdur}:offset={dur_cur - xdur}[v];[0:a][1:a]acrossfade=d={xdur}[a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-c:a", "aac", out]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    current = out

concat_video = current

final = f"{OUT_DIR}/V4_MORGAN_FREEMAN_CINEMATIC_EN.mp4"
cmd_mix = [FFMPEG, "-y", "-i", concat_video, "-i", ambient_path, "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0:weights=1 0.18[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", final]
subprocess.run(cmd_mix, check=True)
print(f"Final V4: {final}")

# Cleanup
for f in segs + temps + [ambient_path] + processed:
    try:
        if os.path.exists(f) and f != concat_video:
            os.remove(f)
    except:
        pass
for f in temps[:-1]:
    try:
        os.remove(f)
    except:
        pass

print("V4 Morgan Freeman complete!")
