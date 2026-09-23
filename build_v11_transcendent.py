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

def make_transcendent_ambient(idx, duration):
    n = int(duration*sr)
    t = np.arange(n)/sr
    base = brown(n, 0.01, seed=idx*10)  # ultra ultra subtle
    # Solfeggio frequencies
    f396 = np.sin(2*np.pi*396*t) * 0.005 * (0.5+0.5*np.sin(2*np.pi*0.012*t))  # liberation
    f432 = np.sin(2*np.pi*432*t) * 0.006 * (0.5+0.5*np.sin(2*np.pi*0.015*t))  # healing
    f528 = np.sin(2*np.pi*528*t) * 0.005 * (0.5+0.5*np.sin(2*np.pi*0.018*t))  # love
    f639 = np.sin(2*np.pi*639*t) * 0.004 * (0.5+0.5*np.sin(2*np.pi*0.02*t))   # connection
    f741 = np.sin(2*np.pi*741*t) * 0.003 * (0.5+0.5*np.sin(2*np.pi*0.022*t))  # awakening
    # Binaural 1Hz delta deepest sleep: left 70Hz, right 71Hz
    binaural_l = np.sin(2*np.pi*70*t) * 0.007
    binaural_r = np.sin(2*np.pi*71*t) * 0.007
    # Sub bass 30Hz + 40Hz + 50Hz for transcendental physical
    sub_30 = np.sin(2*np.pi*30*t) * 0.012
    sub_40 = np.sin(2*np.pi*40*t) * 0.01
    sub_50 = np.sin(2*np.pi*50*t) * 0.006
    
    if idx==0: # station - rain + thunder + all healing
        rain = np.random.randn(n)*0.015
        rain = np.convolve(rain, np.ones(150)/150, mode='same')
        thunder = np.zeros(n)
        for _ in range(int(duration/30)):
            p = random.randint(0,n-6000)
            th = np.sin(2*np.pi*20*np.arange(5000)/sr) * np.exp(-np.arange(5000)/1500) * random.uniform(0.015,0.05)
            thunder[p:p+5000]+=th
        mono = base*0.35 + rain*0.2 + thunder*0.25 + f396*0.4 + f432*0.5 + f528*0.4 + f639*0.3 + f741*0.2 + sub_30*0.5 + sub_40*0.4 + sub_50*0.3
    elif idx==1: # journal - breathing ultra slow 0.12Hz + healing
        breath_lfo = 0.5+0.5*np.sin(2*np.pi*0.12*t)
        breath = brown(n, 0.012, seed=101) * breath_lfo * 0.2
        mono = base*0.4 + breath*0.35 + f396*0.3 + f432*0.6 + f528*0.5 + f639*0.3 + f741*0.2 + sub_30*0.4 + sub_40*0.3 + sub_50*0.2
    elif idx==2: # lake - water + birds + all healing
        lfo = 0.5+0.5*np.sin(2*np.pi*0.15*t)
        water = brown(n, 0.015, seed=200)*(0.3+0.7*lfo)
        birds = np.zeros(n)
        for _ in range(int(duration*0.1)):
            p = random.randint(0,n-3000)
            tt = np.arange(2000)/sr
            f = random.uniform(1600,2400)
            s = np.sin(2*np.pi*f*tt) * np.exp(-tt*6) * random.uniform(0.01,0.04)
            birds[p:p+2000]+=s
        mono = base*0.25 + water*0.3 + birds*0.25 + f396*0.3 + f432*0.6 + f528*0.5 + f639*0.3 + f741*0.2 + sub_30*0.5 + sub_40*0.4 + sub_50*0.3
    elif idx==3: # library - fireplace + tick + healing
        crackle = np.zeros(n)
        for _ in range(int(duration*0.3)):
            p = random.randint(0,n-800)
            l = random.randint(60,300)
            burst = np.random.randn(l)*np.exp(-np.arange(l)/(l/3))*random.uniform(0.015,0.06)
            crackle[p:p+l]+=burst
        tick = np.zeros(n)
        step = int(2.0*sr)
        for p in range(0,n,step):
            if p+80 < n:
                tt = np.arange(80)/sr
                s = np.sin(2*np.pi*40*tt) * np.exp(-tt*10) * 0.025
                tick[p:p+80]+=s
        mono = base*0.3 + crackle*0.2 + tick*0.2 + f396*0.3 + f432*0.6 + f528*0.5 + f639*0.3 + f741*0.2 + sub_30*0.4 + sub_40*0.3 + sub_50*0.2
    else: # cliff - wind + ocean + all healing
        wind_lfo = 0.5+0.5*np.sin(2*np.pi*0.02*t)
        wind = np.random.randn(n)*0.018*wind_lfo
        wind = np.convolve(wind, np.ones(300)/300, mode='same')
        ocean_lfo = 0.5+0.5*np.sin(2*np.pi*0.03*t)
        ocean = brown(n, 0.015, seed=400)*(0.4+0.6*ocean_lfo)
        mono = base*0.2 + wind*0.25 + ocean*0.3 + f396*0.3 + f432*0.6 + f528*0.5 + f639*0.3 + f741*0.2 + sub_30*0.6 + sub_40*0.5 + sub_50*0.4
    
    left = mono + binaural_l*0.5 + brown(n, 0.006, seed=idx*100+1)*0.15
    right = mono + binaural_r*0.5 + brown(n, 0.006, seed=idx*100+2)*0.15
    stereo = np.stack([left,right], axis=1)
    stereo = stereo / (np.max(np.abs(stereo))+1e-6) * 0.08  # ultra subtle 8%
    return stereo

print("Building V11 TRANSCENDENT - even more calm, Solfeggio 396+432+528+639+741 + binaural 1Hz delta")

processed=[]
durations=[]
total=0
for i, audio_path in enumerate(audios):
    out_wav = f"output/v11_voice_{i}.wav"
    # TRANSCENDENT: even slower, softer, warmer, more transcendental
    # atempo 0.85 ultra slow, volume 0.90 softer, warm EQ 60Hz+6 80Hz+5 100Hz+4 120Hz+3, de-ess -5dB, lowpass 5000 ultra warm, compressor 1.2:1 ultra gentle, reverb 60ms 0.10 cozy transcendental
    filt = "atempo=0.85, volume=0.90, equalizer=f=60:t=h:width=1.2:g=6, equalizer=f=80:t=h:width=1.2:g=5, equalizer=f=100:t=h:width=1.2:g=4, equalizer=f=120:t=h:width=1:g=3, equalizer=f=3000:t=h:width=1.2:g=0.5, equalizer=f=5000:t=h:width=2:g=-5, lowpass=f=5000, acompressor=threshold=-28dB:ratio=1.2:attack=50:release=600, aecho=0.8:0.88:60:0.10"
    cmd = [FFMPEG, "-y", "-i", audio_path, "-af", filt, out_wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Voice 87-{i} TRANSCENDENT")

    sr_wav, data = wavfile.read(out_wav)
    if data.ndim>1:
        data = data.mean(axis=1)
    duration = len(data)/sr_wav
    durations.append(duration)
    total+=duration
    print(f"  duration {duration:.2f}s")

    ambient_stereo = make_transcendent_ambient(i, duration+0.3)
    ambient_path = f"output/ambient_v11_{i}.wav"
    wavfile.write(ambient_path, sr, (ambient_stereo*32767).astype(np.int16))

    if data.dtype==np.int16:
        voice_f = data.astype(np.float32)/32767.0
    else:
        voice_f = data.astype(np.float32)/np.max(np.abs(data))
    voice_stereo = np.stack([voice_f, voice_f], axis=1)
    min_len = min(len(voice_stereo), len(ambient_stereo))
    mixed = voice_stereo[:min_len]*0.92 + ambient_stereo[:min_len]*0.25
    mixed = mixed / (np.max(np.abs(mixed))+1e-6) * 0.80
    mixed_path = f"output/v11_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, (mixed*32767).astype(np.int16))

    seg = f"output/v11_seg_{i}.mp4"
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=brightness=0.06:contrast=1.02:saturation=0.7:gamma=1.08,vignette=angle=PI/2:mode=forward"
    cmd = [FFMPEG, "-y", "-loop","1","-i",images[i], "-i", mixed_path, "-vf", vf, "-c:v","libx264","-t",str(duration),"-pix_fmt","yuv444p","-r","24","-c:a","aac","-b:a","128k","-ac","2","-shortest", seg]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  segment {i} done")
    processed.append(seg)

print(f"Total {total:.2f}s")

current = processed[0]
cur_dur = durations[0]
for idx in range(1,len(processed)):
    nxt = processed[idx]
    out = f"output/v11_xfade_{idx}.mp4"
    offset = max(0, cur_dur-3.0)
    cmd = [FFMPEG,"-y","-i",current,"-i",nxt,"-filter_complex",f"[0][1]xfade=transition=fade:duration=3.0:offset={offset},format=yuv444p[v];[0:a][1:a]acrossfade=d=3.0[a]","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv444p","-c:a","aac","-b:a","128k","-ac","2", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cur_dur = cur_dur + durations[idx] - 3.0
    current=out
    print(f"xfade {idx} offset {offset:.2f} new_dur {cur_dur:.2f}")

n_master = int((total+1)*sr)
t_master = np.arange(n_master)/sr
master_left = brown(n_master, 0.012, seed=999) + np.sin(2*np.pi*396*t_master)*0.004 + np.sin(2*np.pi*432*t_master)*0.005 + np.sin(2*np.pi*528*t_master)*0.004 + np.sin(2*np.pi*30*t_master)*0.01 + np.sin(2*np.pi*70*t_master)*0.005
master_right = brown(n_master, 0.012, seed=1000) + np.sin(2*np.pi*396*t_master)*0.004 + np.sin(2*np.pi*432*t_master)*0.005 + np.sin(2*np.pi*528*t_master)*0.004 + np.sin(2*np.pi*30*t_master)*0.01 + np.sin(2*np.pi*71*t_master)*0.005
master_stereo = np.stack([master_left, master_right], axis=1)
master_stereo = master_stereo / (np.max(np.abs(master_stereo))+1e-6) * 0.06
master_path = "output/master_v11.wav"
wavfile.write(master_path, sr, (master_stereo*32767).astype(np.int16))

final = "output/FINAL_V11_TRANSCENDENT.mp4"
cmd = [FFMPEG,"-y","-i",current,"-i",master_path,"-filter_complex","[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 0.20[a]","-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-ac","2", final]
subprocess.run(cmd, check=True)
print(f"FINAL V11 TRANSCENDENT: {final}")

for f in os.listdir("output"):
    if f.startswith("v11_seg_") or f.startswith("v11_xfade_") or f.startswith("v11_mixed_") or f.startswith("ambient_v11_") or f.startswith("v11_voice_") or f.startswith("master_v11"):
        os.remove(os.path.join("output",f))

print("Done V11 TRANSCENDENT")
