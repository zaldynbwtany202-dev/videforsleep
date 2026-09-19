import os, subprocess, numpy as np, random
from scipy.io import wavfile
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
sr = 44100

audios = [
    "audio_v3/ar_01_station.mp3",
    "audio_v3/ar_02_journal.mp3",
    "audio_v3/ar_03_lake.mp3",
    "audio_v3/ar_04_library.mp3",
    "audio_v3/ar_05_cliff.mp3",
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

def gen_rain_drops(duration):
    n = int(duration*sr)
    drops = np.zeros(n)
    num = int(duration*6)
    for _ in range(num):
        pos = random.randint(0, n-1500)
        freq = random.uniform(900, 2200)
        t = np.arange(300)/sr
        env = np.exp(-t*25)
        sine = np.sin(2*np.pi*freq*t) * env * random.uniform(0.08, 0.25)
        drops[pos:pos+300] += sine
    return drops*0.12

def gen_crackle(duration, rate=3.5):
    n = int(duration*sr)
    c = np.zeros(n)
    for _ in range(int(duration*rate)):
        pos = random.randint(0, n-800)
        l = random.randint(150,600)
        burst = np.random.randn(l) * np.exp(-np.arange(l)/(l/3)) * random.uniform(0.15,0.4)
        c[pos:pos+l] += burst
    return c*0.1

def gen_birds(duration):
    n = int(duration*sr)
    b = np.zeros(n)
    for _ in range(int(duration*0.2)):
        pos = random.randint(0, n-2000)
        t = np.arange(1200)/sr
        f = random.uniform(2200, 3200)
        sine = np.sin(2*np.pi*f*t) * np.exp(-t*12) * random.uniform(0.04,0.12)
        b[pos:pos+1200] += sine
    return b

def gen_tick(duration):
    n = int(duration*sr)
    t = np.zeros(n)
    step = int(1.2*sr)
    for p in range(0,n,step):
        if p+150 < n:
            tt = np.arange(150)/sr
            s = np.sin(2*np.pi*55*tt) * np.exp(-tt*18) * 0.06
            t[p:p+150] += s
    return t

def make_ambient(idx, duration):
    n = int(duration*sr)
    t = np.arange(n)/sr
    base = brown(n, 0.035, seed=idx*10)
    if idx==0:
        rain = np.random.randn(n)*0.06
        rain = np.convolve(rain, np.ones(100)/100, mode='same')
        drops = gen_rain_drops(duration)
        wind = brown(n, 0.05, seed=100) * (0.5+0.5*np.sin(2*np.pi*0.04*t))
        rumble = np.sin(2*np.pi*40*t)*0.025
        amb = base + rain*0.5 + drops + wind*0.4 + rumble
    elif idx==1:
        paper = np.random.randn(n)*0.05
        paper = np.convolve(paper, np.ones(30)/30, mode='same') * (0.5+0.5*np.sin(2*np.pi*0.25*t))
        scratch = np.zeros(n)
        for _ in range(int(duration*1.5)):
            p = random.randint(0,n-400)
            sc = np.random.randn(250)*0.08*np.exp(-np.arange(250)/70)
            scratch[p:p+250] += sc
        amb = base*0.4 + paper*0.6 + scratch*0.3
    elif idx==2:
        lfo = 0.5+0.5*np.sin(2*np.pi*0.35*t)
        water = brown(n, 0.06, seed=200)* (0.3+0.7*lfo)
        birds = gen_birds(duration)
        wind = brown(n, 0.04, seed=201)*0.3
        sub = np.sin(2*np.pi*28*t)*0.018
        amb = base*0.3 + water*0.6 + birds + wind + sub
    elif idx==3:
        crackle = gen_crackle(duration, 4)
        tick = gen_tick(duration)
        pages = np.zeros(n)
        for _ in range(int(duration/7)):
            p = random.randint(0,n-2500)
            pg = np.random.randn(1800)*0.12*np.exp(-np.arange(1800)/400)
            pages[p:p+1800] += pg
        fire = brown(n, 0.04, seed=300)*0.4
        amb = base*0.25 + crackle + pages*0.4 + tick*0.5 + fire
    else:
        wind_lfo = 0.5+0.5*np.sin(2*np.pi*0.07*t)
        wind = np.random.randn(n)*0.10*wind_lfo
        wind = np.convolve(wind, np.ones(200)/200, mode='same')
        ocean_lfo = 0.5+0.5*np.sin(2*np.pi*0.06*t)
        ocean = brown(n, 0.07, seed=400)*(0.4+0.6*ocean_lfo)
        gulls = gen_birds(duration)*0.6
        amb = base*0.25 + wind*0.7 + ocean*0.5 + gulls
    amb = amb / (np.max(np.abs(amb))+1e-6) * 0.14
    return amb

print("Building V7 NATURAL ASMR - NO PITCH SHIFT (no squirrel)")

processed=[]
durations=[]
total=0
for i, audio_path in enumerate(audios):
    out_wav = f"output/v7_voice_{i}.wav"
    # NO PITCH SHIFT! Natural human voice 100%
    filt = "atempo=0.98, equalizer=f=120:t=h:width=1.2:g=3, equalizer=f=250:t=h:width=1:g=1.5, equalizer=f=3000:t=h:width=1.2:g=1.5, equalizer=f=6500:t=h:width=2:g=-1.5, lowpass=f=8000, acompressor=threshold=-22dB:ratio=1.8:attack=20:release=250, aecho=0.8:0.88:25:0.05, volume=1.08"
    cmd = [FFMPEG, "-y", "-i", audio_path, "-af", filt, out_wav]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Voice {i} NATURAL no pitch")

    sr_wav, data = wavfile.read(out_wav)
    if data.ndim>1:
        data = data.mean(axis=1)
    duration = len(data)/sr_wav
    durations.append(duration)
    total+=duration
    print(f"  duration {duration:.2f}s")

    ambient = make_ambient(i, duration+0.3)
    left = ambient + brown(len(ambient), 0.015, seed=i*100+1)*0.2
    right = ambient + brown(len(ambient), 0.015, seed=i*100+2)*0.2
    stereo = np.stack([left,right], axis=1)
    stereo = stereo / (np.max(np.abs(stereo))+1e-6) * 0.16
    ambient_path = f"output/ambient_v7_{i}.wav"
    wavfile.write(ambient_path, sr, (stereo*32767).astype(np.int16))

    if data.dtype==np.int16:
        voice_f = data.astype(np.float32)/32767.0
    else:
        voice_f = data.astype(np.float32)/np.max(np.abs(data))
    voice_stereo = np.stack([voice_f, voice_f], axis=1)
    min_len = min(len(voice_stereo), len(stereo))
    mixed = voice_stereo[:min_len]*0.94 + stereo[:min_len]*0.32
    mixed = mixed / (np.max(np.abs(mixed))+1e-6) * 0.86
    mixed_path = f"output/v7_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, (mixed*32767).astype(np.int16))

    seg = f"output/v7_seg_{i}.mp4"
    vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='if(lte(zoom,1.0),1.0,min(zoom+0.0005,1.15))':d=1:s=1920x1080:fps=24,eq=brightness=0.02:contrast=1.07:saturation=0.9,vignette=angle=PI/4:mode=forward,noise=alls=6:allf=t"
    cmd = [FFMPEG, "-y", "-loop","1","-i",images[i], "-i", mixed_path, "-vf", vf, "-c:v","libx264","-t",str(duration),"-pix_fmt","yuv444p","-r","24","-c:a","aac","-b:a","128k","-ac","2","-shortest", seg]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  segment {i} done")
    processed.append(seg)

print(f"Total {total:.2f}s durations {durations}")

# xfade using stored durations
current = processed[0]
cur_dur = durations[0]
for idx in range(1,len(processed)):
    nxt = processed[idx]
    out = f"output/v7_xfade_{idx}.mp4"
    offset = max(0, cur_dur-1.5)
    cmd = [FFMPEG,"-y","-i",current,"-i",nxt,"-filter_complex",f"[0][1]xfade=transition=fade:duration=1.5:offset={offset},format=yuv444p[v];[0:a][1:a]acrossfade=d=1.5[a]","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv444p","-c:a","aac","-b:a","128k","-ac","2", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cur_dur = cur_dur + durations[idx] - 1.5
    current=out
    print(f"xfade {idx} offset {offset:.2f} new_dur {cur_dur:.2f}")

master = brown(int((total+1)*sr), 0.025, seed=999)
master_path = "output/master_v7.wav"
wavfile.write(master_path, sr, (master*0.4*32767).astype(np.int16))

final = "output/FINAL_V7_NATURAL_ASMR.mp4"
cmd = [FFMPEG,"-y","-i",current,"-i",master_path,"-filter_complex","[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 0.12[a]","-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-ac","2", final]
subprocess.run(cmd, check=True)
print(f"FINAL V7 NATURAL ASMR: {final}")

for f in os.listdir("output"):
    if f.startswith("v7_seg_") or f.startswith("v7_xfade_") or f.startswith("v7_mixed_") or f.startswith("ambient_v7_") or f.startswith("v7_voice_") or f.startswith("master_v7"):
        os.remove(os.path.join("output",f))

print("Done V7 - NO SQUIRREL")
