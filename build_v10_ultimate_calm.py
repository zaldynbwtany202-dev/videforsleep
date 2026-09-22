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

def make_ultimate_soothing(idx, duration):
    n = int(duration*sr)
    t = np.arange(n)/sr
    base = brown(n, 0.012, seed=idx*10)  # ultra subtle
    # Healing 432Hz + 528Hz love
    healing_432 = np.sin(2*np.pi*432*t) * 0.006 * (0.5+0.5*np.sin(2*np.pi*0.015*t))
    healing_528 = np.sin(2*np.pi*528*t) * 0.004 * (0.5+0.5*np.sin(2*np.pi*0.018*t))
    # Binaural beat: 2Hz delta for deep sleep (left 80Hz, right 82Hz) - will create stereo later
    binaural_left = np.sin(2*np.pi*80*t) * 0.008
    binaural_right = np.sin(2*np.pi*82*t) * 0.008
    # Sub bass 40Hz + 60Hz for physical comfort
    sub_40 = np.sin(2*np.pi*40*t) * 0.01
    sub_60 = np.sin(2*np.pi*60*t) * 0.006
    
    if idx==0: # station - soft rain + thunder + healing
        rain = np.random.randn(n)*0.018
        rain = np.convolve(rain, np.ones(120)/120, mode='same')
        thunder = np.zeros(n)
        for _ in range(int(duration/25)):
            p = random.randint(0,n-5000)
            th = np.sin(2*np.pi*25*np.arange(4000)/sr) * np.exp(-np.arange(4000)/1200) * random.uniform(0.02,0.06)
            thunder[p:p+4000]+=th
        mono = base*0.4 + rain*0.25 + thunder*0.3 + healing_432*0.5 + healing_528*0.3 + sub_40*0.5 + sub_60*0.3
    elif idx==1: # journal - breathing + room + healing
        breath_lfo = 0.5+0.5*np.sin(2*np.pi*0.15*t)  # slower breathing 0.15Hz
        breath = brown(n, 0.015, seed=101) * breath_lfo * 0.25
        mono = base*0.5 + breath*0.4 + healing_432*0.6 + healing_528*0.4 + sub_40*0.4 + sub_60*0.3
    elif idx==2: # lake - water + birds + healing + binaural
        lfo = 0.5+0.5*np.sin(2*np.pi*0.18*t)
        water = brown(n, 0.018, seed=200)*(0.3+0.7*lfo)
        birds = np.zeros(n)
        for _ in range(int(duration*0.12)):
            p = random.randint(0,n-2500)
            tt = np.arange(1800)/sr
            f = random.uniform(1800,2600)
            s = np.sin(2*np.pi*f*tt) * np.exp(-tt*8) * random.uniform(0.015,0.05)
            birds[p:p+1800]+=s
        mono = base*0.3 + water*0.35 + birds*0.3 + healing_432*0.6 + healing_528*0.4 + sub_40*0.5 + sub_60*0.3
    elif idx==3: # library - fireplace + tick + healing
        crackle = np.zeros(n)
        for _ in range(int(duration*0.4)):
            p = random.randint(0,n-700)
            l = random.randint(80,350)
            burst = np.random.randn(l)*np.exp(-np.arange(l)/(l/3))*random.uniform(0.02,0.08)
            crackle[p:p+l]+=burst
        tick = np.zeros(n)
        step = int(1.8*sr)
        for p in range(0,n,step):
            if p+100 < n:
                tt = np.arange(100)/sr
                s = np.sin(2*np.pi*45*tt) * np.exp(-tt*12) * 0.03
                tick[p:p+100]+=s
        mono = base*0.35 + crackle*0.25 + tick*0.25 + healing_432*0.6 + healing_528*0.4 + sub_40*0.4 + sub_60*0.3
    else: # cliff - wind + ocean + healing
        wind_lfo = 0.5+0.5*np.sin(2*np.pi*0.025*t)
        wind = np.random.randn(n)*0.02*wind_lfo
        wind = np.convolve(wind, np.ones(250)/250, mode='same')
        ocean_lfo = 0.5+0.5*np.sin(2*np.pi*0.035*t)
        ocean = brown(n, 0.018, seed=400)*(0.4+0.6*ocean_lfo)
        mono = base*0.25 + wind*0.3 + ocean*0.35 + healing_432*0.6 + healing_528*0.4 + sub_40*0.6 + sub_60*0.4
    
    # Create stereo with binaural beat: left 80Hz, right 82Hz = 2Hz delta for deep sleep
    left = mono + binaural_left*0.5 + brown(n, 0.008, seed=idx*100+1)*0.2
    right = mono + binaural_right*0.5 + brown(n, 0.008, seed=idx*100+2)*0.2
    stereo = np.stack([left,right], axis=1)
    stereo = stereo / (np.max(np.abs(stereo))+1e-6) * 0.085  # ultra subtle 8.5%
    return stereo

print("Building V10 ULTIMATE CALM - even more calm, comfortable, healing 432Hz+528Hz + binaural 2Hz delta")

processed=[]
durations=[]
total=0
for i, audio_path in enumerate(audios):
    out_wav = f"output/v10_voice_{i}.wav"
    # ULTIMATE CALM: even slower, softer, warmer
    # atempo 0.88 ultra slow calm, volume 0.92 softer, warm EQ 80Hz+5 120Hz+4 250Hz+2, de-ess -4dB, lowpass 5500 ultra warm, compressor 1.3:1 ultra gentle, reverb 50ms 0.08 cozy
    filt = "atempo=0.88, volume=0.92, equalizer=f=80:t=h:width=1.2:g=5, equalizer=f=120:t=h:width=1.2:g=4, equalizer=f=250:t=h:width=1:g=2, equalizer=f=3000:t=h:width=1.2:g=0.8, equalizer=f=5500:t=h:width=2:g=-4, lowpass=f=5500, acompressor=threshold=-26dB:ratio=1.3:attack=40:release=500, aecho=0.8:0.88:50:0.08"
    cmd = [FFMPEG, "-y", "-i", audio_path, "-af", filt, out_wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Voice 87-{i} ULTIMATE CALM")

    sr_wav, data = wavfile.read(out_wav)
    if data.ndim>1:
        data = data.mean(axis=1)
    duration = len(data)/sr_wav
    durations.append(duration)
    total+=duration
    print(f"  duration {duration:.2f}s")

    ambient_stereo = make_ultimate_soothing(i, duration+0.3)
    ambient_path = f"output/ambient_v10_{i}.wav"
    wavfile.write(ambient_path, sr, (ambient_stereo*32767).astype(np.int16))

    if data.dtype==np.int16:
        voice_f = data.astype(np.float32)/32767.0
    else:
        voice_f = data.astype(np.float32)/np.max(np.abs(data))
    voice_stereo = np.stack([voice_f, voice_f], axis=1)
    min_len = min(len(voice_stereo), len(ambient_stereo))
    mixed = voice_stereo[:min_len]*0.94 + ambient_stereo[:min_len]*0.22  # voice 94% calm, ambient 22% soothing
    mixed = mixed / (np.max(np.abs(mixed))+1e-6) * 0.82
    mixed_path = f"output/v10_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, (mixed*32767).astype(np.int16))

    seg = f"output/v10_seg_{i}.mp4"
    # Ultimate calm montage: even slower, warmer, more filmic
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=brightness=0.05:contrast=1.03:saturation=0.75:gamma=1.05,vignette=angle=PI/2.5:mode=forward"
    cmd = [FFMPEG, "-y", "-loop","1","-i",images[i], "-i", mixed_path, "-vf", vf, "-c:v","libx264","-t",str(duration),"-pix_fmt","yuv444p","-r","24","-c:a","aac","-b:a","128k","-ac","2","-shortest", seg]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  segment {i} done")
    processed.append(seg)

print(f"Total {total:.2f}s")

current = processed[0]
cur_dur = durations[0]
for idx in range(1,len(processed)):
    nxt = processed[idx]
    out = f"output/v10_xfade_{idx}.mp4"
    offset = max(0, cur_dur-2.5)  # even longer fade for ultimate calm
    cmd = [FFMPEG,"-y","-i",current,"-i",nxt,"-filter_complex",f"[0][1]xfade=transition=fade:duration=2.5:offset={offset},format=yuv444p[v];[0:a][1:a]acrossfade=d=2.5[a]","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv444p","-c:a","aac","-b:a","128k","-ac","2", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cur_dur = cur_dur + durations[idx] - 2.5
    current=out
    print(f"xfade {idx} offset {offset:.2f} new_dur {cur_dur:.2f}")

# Master ultimate soothing: brown 0.015 + 432Hz + 528Hz + 40Hz + binaural 2Hz
n_master = int((total+1)*sr)
t_master = np.arange(n_master)/sr
master_left = brown(n_master, 0.015, seed=999) + np.sin(2*np.pi*432*t_master)*0.006 + np.sin(2*np.pi*528*t_master)*0.004 + np.sin(2*np.pi*40*t_master)*0.01 + np.sin(2*np.pi*80*t_master)*0.006
master_right = brown(n_master, 0.015, seed=1000) + np.sin(2*np.pi*432*t_master)*0.006 + np.sin(2*np.pi*528*t_master)*0.004 + np.sin(2*np.pi*40*t_master)*0.01 + np.sin(2*np.pi*82*t_master)*0.006
master_stereo = np.stack([master_left, master_right], axis=1)
master_stereo = master_stereo / (np.max(np.abs(master_stereo))+1e-6) * 0.07
master_path = "output/master_v10.wav"
wavfile.write(master_path, sr, (master_stereo*32767).astype(np.int16))

final = "output/FINAL_V10_ULTIMATE_CALM.mp4"
cmd = [FFMPEG,"-y","-i",current,"-i",master_path,"-filter_complex","[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 0.18[a]","-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-ac","2", final]
subprocess.run(cmd, check=True)
print(f"FINAL V10 ULTIMATE CALM: {final}")

for f in os.listdir("output"):
    if f.startswith("v10_seg_") or f.startswith("v10_xfade_") or f.startswith("v10_mixed_") or f.startswith("ambient_v10_") or f.startswith("v10_voice_") or f.startswith("master_v10"):
        os.remove(os.path.join("output",f))

print("Done V10 ULTIMATE CALM - ultra calm, comfortable, healing + binaural")
