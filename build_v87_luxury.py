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
    "assets_v3/v3_01_station.png",
    "assets_v3/v3_02_journal.png",
    "assets_v3/v3_03_lake.png",
    "assets_v3/v3_04_library.png",
    "assets_v3/v3_05_cliff.png",
]

def brown(n, intensity=1.0, seed=None):
    if seed is not None:
        np.random.seed(seed)
    w = np.random.randn(n)
    b = np.cumsum(w)
    b = b - np.mean(b)
    b = b / (np.max(np.abs(b))+1e-6) * intensity
    return b

def make_lux_ambient(idx, duration):
    n = int(duration*sr)
    t = np.arange(n)/sr
    base = brown(n, 0.018, seed=idx*10)  # very subtle luxury
    if idx==0: # station rain luxury - very soft
        rain = np.random.randn(n)*0.025
        rain = np.convolve(rain, np.ones(80)/80, mode='same')
        amb = base*0.4 + rain*0.25
    elif idx==1: # journal luxury silence
        amb = base*0.5
    elif idx==2: # lake luxury water
        lfo = 0.5+0.5*np.sin(2*np.pi*0.25*t)
        water = brown(n, 0.025, seed=200)*(0.3+0.7*lfo)
        amb = base*0.35 + water*0.35
    elif idx==3: # library luxury fireplace very soft
        crackle = np.zeros(n)
        for _ in range(int(duration*0.6)):
            p = random.randint(0,n-600)
            l = random.randint(100,400)
            burst = np.random.randn(l)*np.exp(-np.arange(l)/(l/3))*random.uniform(0.04,0.12)
            crackle[p:p+l]+=burst
        amb = base*0.4 + crackle*0.25
    else: # cliff luxury wind soft
        wind = np.random.randn(n)*0.035*(0.5+0.5*np.sin(2*np.pi*0.04*t))
        wind = np.convolve(wind, np.ones(150)/150, mode='same')
        amb = base*0.35 + wind*0.35
    amb = amb / (np.max(np.abs(amb))+1e-6) * 0.07  # ultra subtle 7%
    return amb

print("Building V87 LUXURY - voice-87 Lexus velvety, ultra natural, no squirrel, luxury ASMR 7%")

processed=[]
durations=[]
total=0
for i, audio_path in enumerate(audios):
    out_wav = f"output/v87_voice_{i}.wav"
    # ULTRA NATURAL LUXURY: raw voice, no pitch, no tempo, keep 100% natural luxurious
    cmd = [FFMPEG, "-y", "-i", audio_path, "-ar", "44100", "-ac", "1", out_wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Voice 87-{i} LUXURY raw natural")

    sr_wav, data = wavfile.read(out_wav)
    if data.ndim>1:
        data = data.mean(axis=1)
    duration = len(data)/sr_wav
    durations.append(duration)
    total+=duration
    print(f"  duration {duration:.2f}s")

    ambient = make_lux_ambient(i, duration+0.2)
    ambient_path = f"output/ambient_v87_{i}.wav"
    wavfile.write(ambient_path, sr, (ambient*32767).astype(np.int16))

    if data.dtype==np.int16:
        voice_f = data.astype(np.float32)/32767.0
    else:
        voice_f = data.astype(np.float32)/np.max(np.abs(data))
    min_len = min(len(voice_f), len(ambient))
    mixed = voice_f[:min_len]*0.98 + ambient[:min_len]*0.12  # voice 98%, ambient 12% ultra subtle
    mixed = mixed / (np.max(np.abs(mixed))+1e-6) * 0.88
    mixed_path = f"output/v87_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, (mixed*32767).astype(np.int16))

    seg = f"output/v87_seg_{i}.mp4"
    # Luxury montage: simple without zoompan to avoid OOM (54s long)
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=brightness=0.02:contrast=1.06:saturation=0.9,vignette=angle=PI/4:mode=forward"
    cmd = [FFMPEG, "-y", "-loop","1","-i",images[i], "-i", mixed_path, "-vf", vf, "-c:v","libx264","-t",str(duration),"-pix_fmt","yuv444p","-r","24","-c:a","aac","-b:a","128k","-shortest", seg]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  segment {i} done")
    processed.append(seg)

print(f"Total {total:.2f}s")

current = processed[0]
cur_dur = durations[0]
for idx in range(1,len(processed)):
    nxt = processed[idx]
    out = f"output/v87_xfade_{idx}.mp4"
    offset = max(0, cur_dur-1.5)
    cmd = [FFMPEG,"-y","-i",current,"-i",nxt,"-filter_complex",f"[0][1]xfade=transition=fade:duration=1.5:offset={offset},format=yuv444p[v];[0:a][1:a]acrossfade=d=1.5[a]","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv444p","-c:a","aac","-b:a","128k", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cur_dur = cur_dur + durations[idx] - 1.5
    current=out
    print(f"xfade {idx} offset {offset:.2f} new_dur {cur_dur:.2f}")

final = "output/FINAL_V87_LUXURY_LEXUS.mp4"
cmd = [FFMPEG,"-y","-i",current,"-c:v","copy","-c:a","aac","-b:a","192k", final]
subprocess.run(cmd, check=True)
print(f"FINAL V87 LUXURY LEXUS: {final}")

for f in os.listdir("output"):
    if f.startswith("v87_seg_") or f.startswith("v87_xfade_") or f.startswith("v87_mixed_") or f.startswith("ambient_v87_") or f.startswith("v87_voice_"):
        os.remove(os.path.join("output",f))

print("Done V87 LUXURY - voice-87 Lexus velvety")
