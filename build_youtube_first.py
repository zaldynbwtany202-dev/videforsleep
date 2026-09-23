import os, subprocess, numpy as np, random
from scipy.io import wavfile
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
sr = 44100

audios = [
    "audio_v3/v87_01_station.mp3",
    "audio_v3/v87_02_journal.mp3",
    "audio_v3/v87_03_lake.mp3",
    "audio_v3/v87_04_library.mp3",
    "audio_v3/v87_05_cliff.mp3",
]
images = [
    "assets_youtube/yt_01_station.png",
    "assets_youtube/yt_02_journal.png",
    "assets_youtube/yt_03_lake.png",
    "assets_youtube/yt_04_library.png",
    "assets_youtube/yt_05_cliff.png",
]

def brown(n, intensity=1.0, seed=None):
    if seed is not None:
        np.random.seed(seed)
    w = np.random.randn(n)
    b = np.cumsum(w)
    b = b - np.mean(b)
    b = b / (np.max(np.abs(b))+1e-6) * intensity
    return b

def make_comfort_ambient(idx, duration):
    n = int(duration*sr)
    t = np.arange(n)/sr
    base = brown(n, 0.008, seed=idx*10)
    f432 = np.sin(2*np.pi*432*t) * 0.004
    sub_30 = np.sin(2*np.pi*30*t) * 0.012
    sub_40 = np.sin(2*np.pi*40*t) * 0.008
    
    if idx==0:
        rain = np.random.randn(n)*0.01
        rain = np.convolve(rain, np.ones(150)/150, mode='same')
        mono = base*0.3 + rain*0.15 + f432*0.3 + sub_30*0.4 + sub_40*0.3
    elif idx==1:
        mono = base*0.35 + f432*0.35 + sub_30*0.3 + sub_40*0.2
    elif idx==2:
        lfo = 0.5+0.5*np.sin(2*np.pi*0.15*t)
        water = brown(n, 0.01, seed=200)*(0.3+0.7*lfo)
        mono = base*0.2 + water*0.2 + f432*0.35 + sub_30*0.4 + sub_40*0.3
    elif idx==3:
        crackle = np.zeros(n)
        for _ in range(int(duration*0.3)):
            p = random.randint(0,n-800)
            l = random.randint(80,300)
            burst = np.random.randn(l)*np.exp(-np.arange(l)/(l/3))*random.uniform(0.02,0.06)
            crackle[p:p+l]+=burst
        mono = base*0.25 + crackle*0.2 + f432*0.35 + sub_30*0.3 + sub_40*0.2
    else:
        wind = np.random.randn(n)*0.012
        wind = np.convolve(wind, np.ones(300)/300, mode='same')
        ocean_lfo = 0.5+0.5*np.sin(2*np.pi*0.04*t)
        ocean = brown(n, 0.01, seed=400)*(0.4+0.6*ocean_lfo)
        mono = base*0.18 + wind*0.12 + ocean*0.18 + f432*0.35 + sub_30*0.5 + sub_40*0.4
    
    left = mono + brown(n, 0.003, seed=idx*100+1)*0.08
    right = mono + brown(n, 0.003, seed=idx*100+2)*0.08
    stereo = np.stack([left,right], axis=1)
    stereo = stereo / (np.max(np.abs(stereo))+1e-6) * 0.06
    return stereo

print("Building YOUTUBE FIRST - comfortable images + deep luxury voice 87 pitch 0.82 no squirrel")

processed=[]
durations=[]
total=0
for i, audio_path in enumerate(audios):
    out_wav = f"output/yt_voice_{i}.wav"
    # Deep luxury no squirrel: pitch 0.82 deeper
    filt = "rubberband=pitch=0.82:tempo=1.0"
    cmd = [FFMPEG, "-y", "-i", audio_path, "-af", filt, out_wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Voice 87-{i} DEEP comfortable")

    sr_wav, data = wavfile.read(out_wav)
    if data.ndim>1:
        data = data.mean(axis=1)
    duration = len(data)/sr_wav
    durations.append(duration)
    total+=duration
    print(f"  duration {duration:.2f}s")

    ambient_stereo = make_comfort_ambient(i, duration+0.2)
    ambient_path = f"output/ambient_yt_{i}.wav"
    wavfile.write(ambient_path, sr, (ambient_stereo*32767).astype(np.int16))

    if data.dtype==np.int16:
        voice_f = data.astype(np.float32)/32767.0
    else:
        voice_f = data.astype(np.float32)/np.max(np.abs(data))
    voice_stereo = np.stack([voice_f, voice_f], axis=1)
    min_len = min(len(voice_stereo), len(ambient_stereo))
    mixed = voice_stereo[:min_len]*0.97 + ambient_stereo[:min_len]*0.12
    mixed = mixed / (np.max(np.abs(mixed))+1e-6) * 0.86
    mixed_path = f"output/yt_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, (mixed*32767).astype(np.int16))

    seg = f"output/yt_seg_{i}.mp4"
    # Comfortable montage: warm, cozy, soft, hygge
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=brightness=0.06:contrast=1.02:saturation=0.9:gamma=1.05,vignette=angle=PI/2.5:mode=forward"
    cmd = [FFMPEG, "-y", "-loop","1","-i",images[i], "-i", mixed_path, "-vf", vf, "-c:v","libx264","-t",str(duration),"-pix_fmt","yuv444p","-r","24","-c:a","aac","-b:a","128k","-ac","2","-shortest", seg]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  segment {i} done")
    processed.append(seg)

print(f"Total {total:.2f}s")

# Simple concat for YouTube
concat_file = "output/yt_concat.txt"
with open(concat_file, "w") as f:
    for seg in processed:
        f.write(f"file '{os.path.basename(seg)}'\n")

cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "output/YOUTUBE_FIRST_COMFORTABLE.mp4"]
subprocess.run(cmd, check=True)
print(f"FINAL YOUTUBE FIRST: output/YOUTUBE_FIRST_COMFORTABLE.mp4")

# Cleanup
for f in os.listdir("output"):
    if f.startswith("yt_seg_") or f.startswith("yt_mixed_") or f.startswith("ambient_yt_") or f.startswith("yt_voice_") or f.startswith("yt_concat"):
        os.remove(os.path.join("output",f))

print("Done YOUTUBE FIRST - comfortable images + deep luxury voice")
