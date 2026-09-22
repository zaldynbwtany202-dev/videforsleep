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

def make_soothing_ambient(idx, duration):
    n = int(duration*sr)
    t = np.arange(n)/sr
    # Base ultra calm brown
    base = brown(n, 0.015, seed=idx*10)
    # Healing 432Hz very subtle
    healing = np.sin(2*np.pi*432*t) * 0.008 * (0.5+0.5*np.sin(2*np.pi*0.02*t))
    # Sub bass 40Hz for comfort
    sub = np.sin(2*np.pi*40*t) * 0.012
    
    if idx==0: # station - soft rain + distant thunder low
        rain = np.random.randn(n)*0.02
        rain = np.convolve(rain, np.ones(100)/100, mode='same')
        # distant thunder: low rumble occasional
        thunder = np.zeros(n)
        for _ in range(int(duration/20)):
            p = random.randint(0,n-4000)
            th = np.sin(2*np.pi*30*np.arange(3000)/sr) * np.exp(-np.arange(3000)/1000) * random.uniform(0.03,0.08)
            thunder[p:p+3000]+=th
        amb = base*0.5 + rain*0.3 + thunder*0.4 + healing*0.5 + sub*0.6
    elif idx==1: # journal - soft room + breathing
        # gentle breathing: slow sine 0.2Hz modulating noise
        breath_lfo = 0.5+0.5*np.sin(2*np.pi*0.18*t)
        breath = brown(n, 0.02, seed=101) * breath_lfo * 0.3
        amb = base*0.6 + breath*0.5 + healing*0.6 + sub*0.5
    elif idx==2: # lake - water + birds + healing
        lfo = 0.5+0.5*np.sin(2*np.pi*0.2*t)
        water = brown(n, 0.02, seed=200)*(0.3+0.7*lfo)
        # soft birds very distant
        birds = np.zeros(n)
        for _ in range(int(duration*0.15)):
            p = random.randint(0,n-2000)
            tt = np.arange(1500)/sr
            f = random.uniform(2000,2800)
            s = np.sin(2*np.pi*f*tt) * np.exp(-tt*10) * random.uniform(0.02,0.06)
            birds[p:p+1500]+=s
        amb = base*0.35 + water*0.4 + birds*0.4 + healing*0.7 + sub*0.6
    elif idx==3: # library - fireplace ultra soft + tick
        crackle = np.zeros(n)
        for _ in range(int(duration*0.5)):
            p = random.randint(0,n-600)
            l = random.randint(100,400)
            burst = np.random.randn(l)*np.exp(-np.arange(l)/(l/3))*random.uniform(0.03,0.10)
            crackle[p:p+l]+=burst
        tick = np.zeros(n)
        step = int(1.5*sr)
        for p in range(0,n,step):
            if p+120 < n:
                tt = np.arange(120)/sr
                s = np.sin(2*np.pi*50*tt) * np.exp(-tt*15) * 0.04
                tick[p:p+120]+=s
        amb = base*0.4 + crackle*0.3 + tick*0.3 + healing*0.6 + sub*0.5
    else: # cliff - wind soft + ocean slow
        wind_lfo = 0.5+0.5*np.sin(2*np.pi*0.03*t)
        wind = np.random.randn(n)*0.025*wind_lfo
        wind = np.convolve(wind, np.ones(200)/200, mode='same')
        ocean_lfo = 0.5+0.5*np.sin(2*np.pi*0.04*t)
        ocean = brown(n, 0.02, seed=400)*(0.4+0.6*ocean_lfo)
        amb = base*0.3 + wind*0.35 + ocean*0.4 + healing*0.6 + sub*0.7
    
    amb = amb / (np.max(np.abs(amb))+1e-6) * 0.09  # soothing low 9%
    return amb

print("Building V9 CALM COMFORT - ultra calm, more comfortable, soothing effects")

processed=[]
durations=[]
total=0
for i, audio_path in enumerate(audios):
    out_wav = f"output/v9_voice_{i}.wav"
    # ULTRA CALM: slower, softer, warmer, more comfortable
    # atempo 0.92 very calm slow, volume 0.95 softer, warm EQ 100Hz+4 200Hz+2, de-ess -3dB, lowpass 6000 warm, compressor 1.5:1 gentle, reverb 40ms 0.06 intimate comfort
    filt = "atempo=0.92, volume=0.95, equalizer=f=100:t=h:width=1.2:g=4, equalizer=f=200:t=h:width=1:g=2, equalizer=f=3000:t=h:width=1.2:g=1, equalizer=f=6000:t=h:width=2:g=-3, lowpass=f=6000, acompressor=threshold=-24dB:ratio=1.5:attack=30:release=400, aecho=0.8:0.88:40:0.06"
    cmd = [FFMPEG, "-y", "-i", audio_path, "-af", filt, out_wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Voice 87-{i} CALM comfort")

    sr_wav, data = wavfile.read(out_wav)
    if data.ndim>1:
        data = data.mean(axis=1)
    duration = len(data)/sr_wav
    durations.append(duration)
    total+=duration
    print(f"  duration {duration:.2f}s")

    ambient = make_soothing_ambient(i, duration+0.3)
    ambient_path = f"output/ambient_v9_{i}.wav"
    wavfile.write(ambient_path, sr, (ambient*32767).astype(np.int16))

    if data.dtype==np.int16:
        voice_f = data.astype(np.float32)/32767.0
    else:
        voice_f = data.astype(np.float32)/np.max(np.abs(data))
    min_len = min(len(voice_f), len(ambient))
    mixed = voice_f[:min_len]*0.96 + ambient[:min_len]*0.18  # voice 96% calm, ambient 18% soothing
    mixed = mixed / (np.max(np.abs(mixed))+1e-6) * 0.85
    mixed_path = f"output/v9_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, (mixed*32767).astype(np.int16))

    seg = f"output/v9_seg_{i}.mp4"
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=brightness=0.04:contrast=1.04:saturation=0.8:gamma=1.03,vignette=angle=PI/3:mode=forward"
    cmd = [FFMPEG, "-y", "-loop","1","-i",images[i], "-i", mixed_path, "-vf", vf, "-c:v","libx264","-t",str(duration),"-pix_fmt","yuv444p","-r","24","-c:a","aac","-b:a","128k","-shortest", seg]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  segment {i} done")
    processed.append(seg)

print(f"Total {total:.2f}s")

current = processed[0]
cur_dur = durations[0]
for idx in range(1,len(processed)):
    nxt = processed[idx]
    out = f"output/v9_xfade_{idx}.mp4"
    offset = max(0, cur_dur-2.0)  # longer fade for more calm transition
    cmd = [FFMPEG,"-y","-i",current,"-i",nxt,"-filter_complex",f"[0][1]xfade=transition=fade:duration=2.0:offset={offset},format=yuv444p[v];[0:a][1:a]acrossfade=d=2.0[a]","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv444p","-c:a","aac","-b:a","128k", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cur_dur = cur_dur + durations[idx] - 2.0
    current=out
    print(f"xfade {idx} offset {offset:.2f} new_dur {cur_dur:.2f}")

# Master soothing bed: brown 0.02 + 432Hz + 40Hz + wind ultra low
n_master = int((total+1)*sr)
t_master = np.arange(n_master)/sr
master = brown(n_master, 0.02, seed=999) + np.sin(2*np.pi*432*t_master)*0.008 + np.sin(2*np.pi*40*t_master)*0.012
master = master / (np.max(np.abs(master))+1e-6) * 0.08
master_path = "output/master_v9.wav"
wavfile.write(master_path, sr, (master*32767).astype(np.int16))

final = "output/FINAL_V9_CALM_COMFORT.mp4"
cmd = [FFMPEG,"-y","-i",current,"-i",master_path,"-filter_complex","[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 0.15[a]","-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k", final]
subprocess.run(cmd, check=True)
print(f"FINAL V9 CALM COMFORT: {final}")

for f in os.listdir("output"):
    if f.startswith("v9_seg_") or f.startswith("v9_xfade_") or f.startswith("v9_mixed_") or f.startswith("ambient_v9_") or f.startswith("v9_voice_") or f.startswith("master_v9"):
        os.remove(os.path.join("output",f))

print("Done V9 CALM COMFORT - ultra calm, comfortable, soothing")
