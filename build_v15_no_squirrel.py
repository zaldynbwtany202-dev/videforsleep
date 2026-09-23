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

def make_soothing_no_squirrel(idx, duration):
    n = int(duration*sr)
    t = np.arange(n)/sr
    base = brown(n, 0.008, seed=idx*10)
    f432 = np.sin(2*np.pi*432*t) * 0.004
    sub_40 = np.sin(2*np.pi*40*t) * 0.008
    binaural_l = np.sin(2*np.pi*40*t) * 0.003
    binaural_r = np.sin(2*np.pi*40.1*t) * 0.003
    
    if idx==0:
        rain = np.random.randn(n)*0.01
        rain = np.convolve(rain, np.ones(150)/150, mode='same')
        mono = base*0.3 + rain*0.15 + f432*0.3 + sub_40*0.4
    elif idx==1:
        mono = base*0.35 + f432*0.35 + sub_40*0.3
    elif idx==2:
        lfo = 0.5+0.5*np.sin(2*np.pi*0.15*t)
        water = brown(n, 0.01, seed=200)*(0.3+0.7*lfo)
        mono = base*0.2 + water*0.2 + f432*0.35 + sub_40*0.4
    elif idx==3:
        mono = base*0.25 + f432*0.35 + sub_40*0.3
    else:
        wind = np.random.randn(n)*0.012
        wind = np.convolve(wind, np.ones(300)/300, mode='same')
        mono = base*0.18 + wind*0.15 + f432*0.35 + sub_40*0.5
    
    left = mono + binaural_l*0.4 + brown(n, 0.003, seed=idx*100+1)*0.1
    right = mono + binaural_r*0.4 + brown(n, 0.003, seed=idx*100+2)*0.1
    stereo = np.stack([left,right], axis=1)
    stereo = stereo / (np.max(np.abs(stereo))+1e-6) * 0.06
    return stereo

print("Building V15 NO SQUIRREL - raw voice 100% natural, no atempo, no pitch, ultra calm")

processed=[]
durations=[]
total=0
for i, audio_path in enumerate(audios):
    out_wav = f"output/v15_voice_{i}.wav"
    # NO SQUIRREL: RAW voice, no atempo, no pitch, no EQ, no reverb - 100% natural
    # Only convert mp3 to wav, keep exactly as TTS generated
    cmd = [FFMPEG, "-y", "-i", audio_path, "-ar", "44100", "-ac", "1", out_wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Voice 87-{i} RAW 100% natural NO SQUIRREL")

    sr_wav, data = wavfile.read(out_wav)
    if data.ndim>1:
        data = data.mean(axis=1)
    duration = len(data)/sr_wav
    durations.append(duration)
    total+=duration
    print(f"  duration {duration:.2f}s")

    ambient_stereo = make_soothing_no_squirrel(i, duration+0.2)
    ambient_path = f"output/ambient_v15_{i}.wav"
    wavfile.write(ambient_path, sr, (ambient_stereo*32767).astype(np.int16))

    if data.dtype==np.int16:
        voice_f = data.astype(np.float32)/32767.0
    else:
        voice_f = data.astype(np.float32)/np.max(np.abs(data))
    voice_stereo = np.stack([voice_f, voice_f], axis=1)
    min_len = min(len(voice_stereo), len(ambient_stereo))
    mixed = voice_stereo[:min_len]*0.97 + ambient_stereo[:min_len]*0.10
    mixed = mixed / (np.max(np.abs(mixed))+1e-6) * 0.86
    mixed_path = f"output/v15_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, (mixed*32767).astype(np.int16))

    seg = f"output/v15_seg_{i}.mp4"
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=brightness=0.02:contrast=1.04:saturation=0.85,vignette=angle=PI/3:mode=forward"
    cmd = [FFMPEG, "-y", "-loop","1","-i",images[i], "-i", mixed_path, "-vf", vf, "-c:v","libx264","-t",str(duration),"-pix_fmt","yuv444p","-r","24","-c:a","aac","-b:a","128k","-ac","2","-shortest", seg]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  segment {i} done")
    processed.append(seg)

print(f"Total {total:.2f}s")

current = processed[0]
cur_dur = durations[0]
for idx in range(1,len(processed)):
    nxt = processed[idx]
    out = f"output/v15_xfade_{idx}.mp4"
    offset = max(0, cur_dur-1.5)
    cmd = [FFMPEG,"-y","-i",current,"-i",nxt,"-filter_complex",f"[0][1]xfade=transition=fade:duration=1.5:offset={offset},format=yuv444p[v];[0:a][1:a]acrossfade=d=1.5[a]","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv444p","-c:a","aac","-b:a","128k","-ac","2", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cur_dur = cur_dur + durations[idx] - 1.5
    current=out
    print(f"xfade {idx} offset {offset:.2f} new_dur {cur_dur:.2f}")

final = "output/FINAL_V15_NO_SQUIRREL.mp4"
cmd = [FFMPEG,"-y","-i",current,"-c:v","copy","-c:a","aac","-b:a","192k","-ac","2", final]
subprocess.run(cmd, check=True)
print(f"FINAL V15 NO SQUIRREL: {final}")

for f in os.listdir("output"):
    if f.startswith("v15_seg_") or f.startswith("v15_xfade_") or f.startswith("v15_mixed_") or f.startswith("ambient_v15_") or f.startswith("v15_voice_"):
        os.remove(os.path.join("output",f))

print("Done V15 NO SQUIRREL - raw voice 100% natural")
