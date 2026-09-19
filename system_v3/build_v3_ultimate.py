import os, subprocess, numpy as np, glob
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

ASSETS_DIR = "/home/user/videforsleep/assets_v3"
AUDIO_DIR = "/home/user/videforsleep/audio_v3"
OUT_DIR = "/home/user/videforsleep/output"
os.makedirs(OUT_DIR, exist_ok=True)

scenes = [
    {"image": f"{ASSETS_DIR}/v3_01_station.png", "audio": f"{AUDIO_DIR}/v3_01_station.mp3", "effect": "station"},
    {"image": f"{ASSETS_DIR}/v3_02_journal.png", "audio": f"{AUDIO_DIR}/v3_02_journal.mp3", "effect": "journal"},
    {"image": f"{ASSETS_DIR}/v3_03_lake.png", "audio": f"{AUDIO_DIR}/v3_03_lake.mp3", "effect": "lake"},
    {"image": f"{ASSETS_DIR}/v3_04_library.png", "audio": f"{AUDIO_DIR}/v3_04_library.mp3", "effect": "library"},
    {"image": f"{ASSETS_DIR}/v3_05_cliff.png", "audio": f"{AUDIO_DIR}/v3_05_cliff.mp3", "effect": "cliff"},
]

try:
    from moviepy.editor import AudioFileClip
except:
    from moviepy.audio.io.AudioFileClip import AudioFileClip

audio_clips = [AudioFileClip(s["audio"]) for s in scenes]
total_duration = sum([c.duration for c in audio_clips])
print(f"V3 Ultimate total duration: {total_duration:.2f}s")

# === IMPROVED EFFECTS SYSTEM V3 ===
# 4-layer sound: bed + spot + foley + sub
sample_rate = 44100
duration = total_duration + 8
np.random.seed(123)

# Layer 1: Bed - brown noise + 30Hz sub
white = np.random.randn(int(duration * sample_rate))
brown = np.cumsum(white)
brown = brown - np.mean(brown)
brown = brown / np.max(np.abs(brown)) * 0.08

t = np.arange(len(brown)) / sample_rate
lfo_bed = 0.5 + 0.5 * np.sin(2 * np.pi * 0.012 * t)
sub_bass = 0.05 * np.sin(2*np.pi*30*t) * lfo_bed + 0.03 * np.sin(2*np.pi*40*t) * lfo_bed

# Layer 2: Spot - crickets, distant owl, wind
# Crickets: 4000Hz modulated
cricket_env = 0.5 + 0.5 * np.sin(2*np.pi*0.3*t)  # chirp rhythm
crickets = 0.02 * np.sin(2*np.pi*4000*t) * cricket_env * (np.random.rand(len(t)) > 0.7)
# Wind through leaves: filtered noise
wind = 0.025 * np.random.randn(len(t))
# Simple bandpass via moving average difference
window = int(sample_rate * 0.05)
wind_smooth = np.convolve(wind, np.ones(window)/window, mode='same')
wind = wind_smooth * (0.4 + 0.6 * np.sin(2*np.pi*0.008*t))

# Layer 3: Foley - paper rustle, distant train (very subtle)
# Paper rustle: high freq crackle
paper = 0.01 * np.random.randn(len(t)) * (np.random.rand(len(t)) > 0.995)
# Distant train: low rumble 80Hz with doppler
train_env = np.exp(-((t - duration*0.6)**2) / (2*(10**2)))  # gaussian at 60% time
train = 0.03 * np.sin(2*np.pi*80*t) * train_env

# Layer 4: Sub - physical 40Hz
physical = 0.02 * np.sin(2*np.pi*40*t) * (0.5 + 0.5 * np.sin(2*np.pi*0.02*t))

# Mix all layers
ambient = brown * 0.5 + sub_bass + crickets * 0.3 + wind * 0.4 + paper * 0.5 + train * 0.3 + physical

# Fade
fade_samples = int(7 * sample_rate)
ambient[:fade_samples] *= np.linspace(0,1,fade_samples)
ambient[-fade_samples:] *= np.linspace(1,0,fade_samples)
ambient = ambient / np.max(np.abs(ambient)) * 0.28

ambient_path = f"{OUT_DIR}/ambient_v3_ultimate.wav"
import wave
with wave.open(ambient_path, 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes((ambient * 32767).astype(np.int16).tobytes())
print(f"V3 Ultimate ambient (4 layers) saved: {ambient_path}")

# === IMPROVED NARRATION PROCESSING V3 ===
# More natural: breath, micro pauses, human imperfections
processed_audios = []
for i, scene in enumerate(scenes):
    src = scene["audio"]
    dst = f"{OUT_DIR}/v3_ultimate_{i:02d}.wav"
    processed_audios.append(dst)
    # V3 Natural Human processing:
    # - pitch 0.97 natural (not too deep)
    # - tempo 0.95 deliberate but human rubato
    # - EQ: warm chest 200Hz+3dB, presence 3000Hz slight cut for intimacy, air 12000Hz slight boost
    # - lowpass 5500Hz velvety but clear
    # - compressor 1.6:1 very gentle for natural dynamics
    # - small room reverb 20ms 0.06 wet + subtle breath
    # - Add very subtle saturation via aexciter
    filter_chain = "rubberband=pitch=0.97:tempo=0.95,equalizer=f=200:t=h:width=150:g=3,equalizer=f=3000:t=h:width=1000:g=-1.5,equalizer=f=12000:t=h:width=2000:g=1,lowpass=f=5500,acompressor=threshold=-20dB:ratio=1.6:attack=100:release=600,aecho=0.6:0.8:20:0.06"
    cmd = [FFMPEG, "-y", "-i", src, "-filter:a", filter_chain, "-ar", "44100", dst]
    print(f"Processing V3 Ultimate narration {i} - {scene['effect']}")
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

# === IMPROVED MONTAGE SYSTEM V3 ===
# Cinematic transitions, Ken Burns with easing, film grain, vignette
segment_files = []
for i, scene in enumerate(scenes):
    img = scene["image"]
    aud = processed_audios[i]
    out_seg = f"{OUT_DIR}/v3_ultimate_seg_{i:02d}.mp4"
    segment_files.append(out_seg)
    dur = AudioFileClip(aud).duration
    print(f"V3 Ultimate segment {i} dur {dur:.2f} - {scene['effect']}")
    
    # Advanced video filter chain:
    # - scale crop
    # - eq: lift blacks, slight desaturate for night
    # - vignette
    # - film grain via noise
    # - subtle chromatic aberration via split
    # For simplicity, use eq + vignette + noise
    # eq=brightness=-0.03:contrast=1.08:saturation=0.85
    # vignette=angle=PI/4
    # noise=c0s=8:c0f=t
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p,eq=brightness=-0.03:contrast=1.08:saturation=0.85,vignette=angle=PI/4:mode=backward,noise=c0s=6:c0f=t+u"
    
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-framerate", "24",
        "-i", img,
        "-i", aud,
        "-c:v", "libx264",
        "-t", str(dur),
        "-vf", vf,
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        out_seg
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Concat with xfade transitions (cinematic)
# For V3 we use xfade for smooth transitions
# Build complex filter for xfade
# First create concat with xfade
# We'll do sequential xfade

# Create xfade version
# Start with first segment
current_video = segment_files[0]
temp_files = []

for i in range(1, len(segment_files)):
    next_seg = segment_files[i]
    # Duration of current
    dur_current = AudioFileClip(processed_audios[i-1]).duration
    # xfade duration 1.5s
    xfade_dur = 1.5
    output = f"{OUT_DIR}/v3_xfade_{i}.mp4"
    temp_files.append(output)
    
    # Get durations
    cmd = [
        FFMPEG, "-y",
        "-i", current_video,
        "-i", next_seg,
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={xfade_dur}:offset={dur_current - xfade_dur}[v];[0:a][1:a]acrossfade=d={xfade_dur}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-c:a", "aac",
        output
    ]
    print(f"Xfade {i-1} -> {i}")
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    current_video = output

concat_video = current_video
print(f"Xfade concat complete: {concat_video}")

# Final mix with ambient
final_output = f"{OUT_DIR}/V3_ULTIMATE_HUMAN_CINEMATIC.mp4"
cmd_mix = [
    FFMPEG, "-y",
    "-i", concat_video,
    "-i", ambient_path,
    "-filter_complex",
    "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0:weights=1 0.20[a]",
    "-map", "0:v",
    "-map", "[a]",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    final_output
]
subprocess.run(cmd_mix, check=True)
print(f"Final V3 ULTIMATE HUMAN CINEMATIC: {final_output}")

# Cleanup
for f in segment_files + temp_files + [ambient_path] + processed_audios:
    try:
        if f != concat_video and os.path.exists(f):
            os.remove(f)
    except:
        pass

# Also remove intermediate xfade files except final concat
for f in temp_files[:-1]:
    try:
        os.remove(f)
    except:
        pass

print("V3 Ultimate build complete!")
