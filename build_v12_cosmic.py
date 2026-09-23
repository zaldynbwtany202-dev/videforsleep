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

def make_cosmic_ambient(idx, duration):
    n = int(duration*sr)
    t = np.arange(n)/sr
    base = brown(n, 0.008, seed=idx*10)  # ultra ultra ultra subtle
    # Full 9 Solfeggio
    f174 = np.sin(2*np.pi*174*t) * 0.004 * (0.5+0.5*np.sin(2*np.pi*0.01*t))   # foundation
    f285 = np.sin(2*np.pi*285*t) * 0.004 * (0.5+0.5*np.sin(2*np.pi*0.012*t))  # quantum
    f396 = np.sin(2*np.pi*396*t) * 0.0045 * (0.5+0.5*np.sin(2*np.pi*0.014*t)) # liberation
    f417 = np.sin(2*np.pi*417*t) * 0.004 * (0.5+0.5*np.sin(2*np.pi*0.016*t))  # change
    f432 = np.sin(2*np.pi*432*t) * 0.005 * (0.5+0.5*np.sin(2*np.pi*0.018*t))  # healing
    f528 = np.sin(2*np.pi*528*t) * 0.0045 * (0.5+0.5*np.sin(2*np.pi*0.02*t))  # love
    f639 = np.sin(2*np.pi*639*t) * 0.0035 * (0.5+0.5*np.sin(2*np.pi*0.022*t)) # connection
    f741 = np.sin(2*np.pi*741*t) * 0.003 * (0.5+0.5*np.sin(2*np.pi*0.024*t))  # awakening
    f852 = np.sin(2*np.pi*852*t) * 0.0025 * (0.5+0.5*np.sin(2*np.pi*0.026*t)) # intuition
    f963 = np.sin(2*np.pi*963*t) * 0.002 * (0.5+0.5*np.sin(2*np.pi*0.028*t))  # divine
    # Binaural 0.5Hz epsilon deepest meditation: left 60Hz, right 60.5Hz
    binaural_l = np.sin(2*np.pi*60*t) * 0.006
    binaural_r = np.sin(2*np.pi*60.5*t) * 0.006
    # Sub bass cosmic 20Hz+30Hz+40Hz
    sub_20 = np.sin(2*np.pi*20*t) * 0.015
    sub_30 = np.sin(2*np.pi*30*t) * 0.01
    sub_40 = np.sin(2*np.pi*40*t) * 0.008
    
    if idx==0:
        rain = np.random.randn(n)*0.012
        rain = np.convolve(rain, np.ones(180)/180, mode='same')
        thunder = np.zeros(n)
        for _ in range(int(duration/35)):
            p = random.randint(0,n-7000)
            th = np.sin(2*np.pi*18*np.arange(6000)/sr) * np.exp(-np.arange(6000)/1800) * random.uniform(0.01,0.04)
            thunder[p:p+6000]+=th
        mono = base*0.3 + rain*0.15 + thunder*0.2 + f174*0.3 + f285*0.3 + f396*0.35 + f417*0.3 + f432*0.4 + f528*0.35 + f639*0.25 + f741*0.2 + f852*0.15 + f963*0.1 + sub_20*0.5 + sub_30*0.4 + sub_40*0.3
    elif idx==1:
        breath_lfo = 0.5+0.5*np.sin(2*np.pi*0.10*t)  # ultra slow breathing
        breath = brown(n, 0.01, seed=101) * breath_lfo * 0.18
        mono = base*0.35 + breath*0.3 + f174*0.25 + f285*0.25 + f396*0.25 + f417*0.25 + f432*0.5 + f528*0.4 + f639*0.25 + f741*0.2 + f852*0.15 + f963*0.1 + sub_20*0.4 + sub_30*0.3 + sub_40*0.2
    elif idx==2:
        lfo = 0.5+0.5*np.sin(2*np.pi*0.12*t)
        water = brown(n, 0.012, seed=200)*(0.3+0.7*lfo)
        birds = np.zeros(n)
        for _ in range(int(duration*0.08)):
            p = random.randint(0,n-3500)
            tt = np.arange(2200)/sr
            f = random.uniform(1400,2200)
            s = np.sin(2*np.pi*f*tt) * np.exp(-tt*5) * random.uniform(0.008,0.03)
            birds[p:p+2200]+=s
        mono = base*0.2 + water*0.25 + birds*0.2 + f174*0.25 + f285*0.25 + f396*0.25 + f417*0.25 + f432*0.5 + f528*0.4 + f639*0.25 + f741*0.2 + f852*0.15 + f963*0.1 + sub_20*0.5 + sub_30*0.4 + sub_40*0.3
    elif idx==3:
        crackle = np.zeros(n)
        for _ in range(int(duration*0.25)):
            p = random.randint(0,n-900)
            l = random.randint(50,250)
            burst = np.random.randn(l)*np.exp(-np.arange(l)/(l/3))*random.uniform(0.01,0.05)
            crackle[p:p+l]+=burst
        tick = np.zeros(n)
        step = int(2.2*sr)
        for p in range(0,n,step):
            if p+60 < n:
                tt = np.arange(60)/sr
                s = np.sin(2*np.pi*35*tt) * np.exp(-tt*8) * 0.02
                tick[p:p+60]+=s
        mono = base*0.25 + crackle*0.15 + tick*0.15 + f174*0.25 + f285*0.25 + f396*0.25 + f417*0.25 + f432*0.5 + f528*0.4 + f639*0.25 + f741*0.2 + f852*0.15 + f963*0.1 + sub_20*0.4 + sub_30*0.3 + sub_40*0.2
    else:
        wind_lfo = 0.5+0.5*np.sin(2*np.pi*0.018*t)
        wind = np.random.randn(n)*0.015*wind_lfo
        wind = np.convolve(wind, np.ones(350)/350, mode='same')
        ocean_lfo = 0.5+0.5*np.sin(2*np.pi*0.025*t)
        ocean = brown(n, 0.012, seed=400)*(0.4+0.6*ocean_lfo)
        mono = base*0.18 + wind*0.2 + ocean*0.25 + f174*0.25 + f285*0.25 + f396*0.25 + f417*0.25 + f432*0.5 + f528*0.4 + f639*0.25 + f741*0.2 + f852*0.15 + f963*0.1 + sub_20*0.6 + sub_30*0.5 + sub_40*0.4
    
    left = mono + binaural_l*0.5 + brown(n, 0.005, seed=idx*100+1)*0.12
    right = mono + binaural_r*0.5 + brown(n, 0.005, seed=idx*100+2)*0.12
    stereo = np.stack([left,right], axis=1)
    stereo = stereo / (np.max(np.abs(stereo))+1e-6) * 0.075  # ultra subtle 7.5%
    return stereo

print("Building V12 COSMIC - ultimate calm, 9 Solfeggio + binaural 0.5Hz epsilon + sub 20Hz")

processed=[]
durations=[]
total=0
for i, audio_path in enumerate(audios):
    out_wav = f"output/v12_voice_{i}.wav"
    # COSMIC: even slower, softer, warmer, more cosmic
    # atempo 0.82 ultra slow, volume 0.88 softer, warm EQ 50Hz+7 60Hz+6 80Hz+5 100Hz+4 120Hz+3, de-ess -6dB, lowpass 4500 ultra warm, compressor 1.1:1 ultra gentle, reverb 70ms 0.12 cozy cosmic
    filt = "atempo=0.82, volume=0.88, equalizer=f=50:t=h:width=1.2:g=7, equalizer=f=60:t=h:width=1.2:g=6, equalizer=f=80:t=h:width=1.2:g=5, equalizer=f=100:t=h:width=1.2:g=4, equalizer=f=120:t=h:width=1:g=3, equalizer=f=3000:t=h:width=1.2:g=0.3, equalizer=f=4500:t=h:width=2:g=-6, lowpass=f=4500, acompressor=threshold=-30dB:ratio=1.1:attack=60:release=700, aecho=0.8:0.88:70:0.12"
    cmd = [FFMPEG, "-y", "-i", audio_path, "-af", filt, out_wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Voice 87-{i} COSMIC")

    sr_wav, data = wavfile.read(out_wav)
    if data.ndim>1:
        data = data.mean(axis=1)
    duration = len(data)/sr_wav
    durations.append(duration)
    total+=duration
    print(f"  duration {duration:.2f}s")

    ambient_stereo = make_cosmic_ambient(i, duration+0.3)
    ambient_path = f"output/ambient_v12_{i}.wav"
    wavfile.write(ambient_path, sr, (ambient_stereo*32767).astype(np.int16))

    if data.dtype==np.int16:
        voice_f = data.astype(np.float32)/32767.0
    else:
        voice_f = data.astype(np.float32)/np.max(np.abs(data))
    voice_stereo = np.stack([voice_f, voice_f], axis=1)
    min_len = min(len(voice_stereo), len(ambient_stereo))
    mixed = voice_stereo[:min_len]*0.90 + ambient_stereo[:min_len]*0.28
    mixed = mixed / (np.max(np.abs(mixed))+1e-6) * 0.78
    mixed_path = f"output/v12_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, (mixed*32767).astype(np.int16))

    seg = f"output/v12_seg_{i}.mp4"
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=brightness=0.07:contrast=1.01:saturation=0.65:gamma=1.10,vignette=angle=PI/1.8:mode=forward"
    cmd = [FFMPEG, "-y", "-loop","1","-i",images[i], "-i", mixed_path, "-vf", vf, "-c:v","libx264","-t",str(duration),"-pix_fmt","yuv444p","-r","24","-c:a","aac","-b:a","128k","-ac","2","-shortest", seg]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  segment {i} done")
    processed.append(seg)

print(f"Total {total:.2f}s")

current = processed[0]
cur_dur = durations[0]
for idx in range(1,len(processed)):
    nxt = processed[idx]
    out = f"output/v12_xfade_{idx}.mp4"
    offset = max(0, cur_dur-3.5)
    cmd = [FFMPEG,"-y","-i",current,"-i",nxt,"-filter_complex",f"[0][1]xfade=transition=fade:duration=3.5:offset={offset},format=yuv444p[v];[0:a][1:a]acrossfade=d=3.5[a]","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv444p","-c:a","aac","-b:a","128k","-ac","2", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cur_dur = cur_dur + durations[idx] - 3.5
    current=out
    print(f"xfade {idx} offset {offset:.2f} new_dur {cur_dur:.2f}")

n_master = int((total+1)*sr)
t_master = np.arange(n_master)/sr
master_left = brown(n_master, 0.01, seed=999) + np.sin(2*np.pi*174*t_master)*0.003 + np.sin(2*np.pi*396*t_master)*0.003 + np.sin(2*np.pi*432*t_master)*0.004 + np.sin(2*np.pi*528*t_master)*0.003 + np.sin(2*np.pi*20*t_master)*0.012 + np.sin(2*np.pi*60*t_master)*0.004
master_right = brown(n_master, 0.01, seed=1000) + np.sin(2*np.pi*174*t_master)*0.003 + np.sin(2*np.pi*396*t_master)*0.003 + np.sin(2*np.pi*432*t_master)*0.004 + np.sin(2*np.pi*528*t_master)*0.003 + np.sin(2*np.pi*20*t_master)*0.012 + np.sin(2*np.pi*60.5*t_master)*0.004
master_stereo = np.stack([master_left, master_right], axis=1)
master_stereo = master_stereo / (np.max(np.abs(master_stereo))+1e-6) * 0.055
master_path = "output/master_v12.wav"
wavfile.write(master_path, sr, (master_stereo*32767).astype(np.int16))

final = "output/FINAL_V12_COSMIC.mp4"
cmd = [FFMPEG,"-y","-i",current,"-i",master_path,"-filter_complex","[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 0.22[a]","-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-ac","2", final]
subprocess.run(cmd, check=True)
print(f"FINAL V12 COSMIC: {final}")

for f in os.listdir("output"):
    if f.startswith("v12_seg_") or f.startswith("v12_xfade_") or f.startswith("v12_mixed_") or f.startswith("ambient_v12_") or f.startswith("v12_voice_") or f.startswith("master_v12"):
        os.remove(os.path.join("output",f))

print("Done V12 COSMIC")
