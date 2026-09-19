import os, subprocess, numpy as np, random
from scipy.io import wavfile

# Config
sr = 44100
FFMPEG = __import__('imageio_ffmpeg').get_ffmpeg_exe()

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
durations_estimate = [31, 26, 24, 28, 33]  # approximate

def brown_noise(n, intensity=1.0, seed=None):
    if seed is not None:
        np.random.seed(seed)
    white = np.random.randn(n)
    brown = np.cumsum(white)
    brown = brown - np.mean(brown)
    brown = brown / np.max(np.abs(brown)) * intensity
    return brown

def filtered_noise(n, low, high, intensity=1.0):
    white = np.random.randn(n)
    # simple bandpass via cumulative? Use crude filter: we will use ffmpeg later, here just white with envelope
    # For now return white * intensity with some smoothing
    # Smooth with moving average for lowpass effect
    if high < 1000:
        # lowpass: smooth
        kernel = int(sr / high)
        if kernel > 1:
            white = np.convolve(white, np.ones(kernel)/kernel, mode='same')
    return white * intensity

def generate_rain_drops(duration, sr):
    n = int(duration * sr)
    drops = np.zeros(n)
    num_drops = int(duration * 8)  # 8 drops per second avg
    for _ in range(num_drops):
        pos = random.randint(0, n-2000)
        freq = random.uniform(800, 2500)
        t = np.arange(200) / sr
        envelope = np.exp(-t * 30)
        sine = np.sin(2 * np.pi * freq * t) * envelope * random.uniform(0.1, 0.4)
        drops[pos:pos+200] += sine
    return drops * 0.15

def generate_crackle(duration, sr, rate=3):
    n = int(duration * sr)
    crackle = np.zeros(n)
    num = int(duration * rate)
    for _ in range(num):
        pos = random.randint(0, n-1000)
        length = random.randint(200, 800)
        # exponential decay noise burst
        burst = np.random.randn(length) * np.exp(-np.arange(length)/ (length/4)) * random.uniform(0.2, 0.6)
        crackle[pos:pos+length] += burst
    return crackle * 0.12

def generate_chirps(duration, sr, freq=2500, rate=0.3):
    n = int(duration * sr)
    chirps = np.zeros(n)
    num = int(duration * rate)
    for _ in range(num):
        pos = random.randint(0, n-2000)
        t = np.arange(1500) / sr
        # chirp with vibrato
        vibrato = 1 + 0.3 * np.sin(2*np.pi*20*t)
        sine = np.sin(2*np.pi*freq*vibrato*t) * np.exp(-t*15) * random.uniform(0.05, 0.15)
        chirps[pos:pos+1500] += sine
    return chirps

def generate_tick(duration, sr, interval=1.0):
    n = int(duration * sr)
    tick = np.zeros(n)
    step = int(interval * sr)
    for pos in range(0, n, step):
        if pos+200 < n:
            t = np.arange(200)/sr
            # low thump
            sine = np.sin(2*np.pi*60*t) * np.exp(-t*20) * 0.08
            tick[pos:pos+200] += sine
    return tick

def generate_wave_lfo(duration, sr, freq=0.07, intensity=1.0):
    n = int(duration * sr)
    t = np.arange(n)/sr
    lfo = (np.sin(2*np.pi*freq*t) + 1) * 0.5  # 0-1
    # smooth lfo
    return lfo * intensity

# Generate immersive ASMR ambients per scene
def make_ambient(scene_idx, duration):
    n = int(duration * sr)
    t = np.arange(n)/sr
    # base brown
    base = brown_noise(n, 0.04, seed=scene_idx*10)
    
    if scene_idx == 0:  # station rain night
        rain_noise = filtered_noise(n, 1000, 4000, 0.08)
        drops = generate_rain_drops(duration, sr)
        wind_lfo = generate_wave_lfo(duration, sr, 0.05, 0.06)
        wind = brown_noise(n, 1.0, seed=100) * wind_lfo
        # low rumble train distant
        rumble = np.sin(2*np.pi*45*t) * 0.03 * (0.5 + 0.5*np.sin(2*np.pi*0.02*t))
        # combine
        ambient = base + rain_noise*0.6 + drops + wind*0.5 + rumble
        desc = "station rain ASMR"
    elif scene_idx == 1:  # journal
        paper = filtered_noise(n, 1500, 4000, 0.06)
        # random paper rustle envelopes
        envelope = generate_wave_lfo(duration, sr, 0.3, 1.0)
        paper = paper * envelope * 0.5
        # pencil writing clicks
        pencil = np.zeros(n)
        for _ in range(int(duration*2)):
            pos = random.randint(0, n-500)
            # rapid scratch
            scratch = np.random.randn(300) * 0.1 * np.exp(-np.arange(300)/80)
            pencil[pos:pos+300] += scratch
        ambient = base*0.5 + paper*0.7 + pencil*0.4
        desc = "journal paper ASMR"
    elif scene_idx == 2:  # lake
        water_lfo = generate_wave_lfo(duration, sr, 0.4, 1.0)
        water = brown_noise(n, 0.07, seed=200) * (0.3 + 0.7*water_lfo)
        birds = generate_chirps(duration, sr, 2500, 0.25)
        wind_trees = filtered_noise(n, 200, 800, 0.05) * generate_wave_lfo(duration, sr, 0.12, 1.0)
        sub = np.sin(2*np.pi*30*t) * 0.02
        ambient = base*0.4 + water*0.6 + birds + wind_trees*0.4 + sub
        desc = "lake water ASMR"
    elif scene_idx == 3:  # library fireplace
        crackle = generate_crackle(duration, sr, 4)
        page_turns = np.zeros(n)
        for _ in range(int(duration/6)):
            pos = random.randint(0, n-3000)
            burst = np.random.randn(2000) * 0.15 * np.exp(-np.arange(2000)/500)
            page_turns[pos:pos+2000] += burst
        tick = generate_tick(duration, sr, 1.2)
        fire_low = brown_noise(n, 0.05, seed=300) * 0.5
        ambient = base*0.3 + crackle + page_turns*0.5 + tick*0.6 + fire_low
        desc = "library fireplace ASMR"
    else:  # cliff
        strong_wind_lfo = generate_wave_lfo(duration, sr, 0.08, 1.0)
        wind = filtered_noise(n, 100, 1000, 0.12) * strong_wind_lfo
        wave_lfo = generate_wave_lfo(duration, sr, 0.07, 1.0)
        ocean = brown_noise(n, 0.08, seed=400) * (0.4 + 0.6*wave_lfo) + np.sin(2*np.pi*0.07*t)*0.02
        gulls = generate_chirps(duration, sr, 1800, 0.15)
        ambient = base*0.3 + wind*0.8 + ocean*0.6 + gulls*0.7
        desc = "cliff wind ocean ASMR"
    
    # Normalize
    ambient = ambient / (np.max(np.abs(ambient)) + 1e-6) * 0.15
    print(f"Ambient {scene_idx} {desc}: max {np.max(np.abs(ambient)):.3f}")
    return ambient

# Process voices with improved ASMR quality
os.makedirs("output", exist_ok=True)
processed = []
total_dur = 0

for i, audio_path in enumerate(audios):
    dur_est = durations_estimate[i]
    # Improved voice processing: warm, intimate, close-mic, ASMR
    out_wav = f"output/v6_asmr_voice_{i}.wav"
    # pitch 0.99 natural, tempo 0.95 slightly slower for ASMR, warm EQ, de-ess, intimate reverb
    cmd = [
        FFMPEG, "-y", "-i", audio_path,
        "-af",
        # rubberband pitch 0.99 tempo 0.95, EQ warm chest 100Hz+4 200Hz+2 2800Hz+2, high shelf -2dB, lowpass 7000, compressor 2:1, reverb small room 35ms 0.07, volume 1.1
        "rubberband=pitch=0.99:tempo=0.95, equalizer=f=100:t=h:width=1.2:g=4, equalizer=f=200:t=h:width=1:g=2, equalizer=f=2800:t=h:width=1.5:g=2, equalizer=f=6500:t=h:width=2:g=-2, lowpass=f=7000, acompressor=threshold=-20dB:ratio=2:attack=10:release=150, aecho=0.8:0.88:35:0.07, volume=1.15",
        out_wav
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Processed ASMR voice {i}")

    # Get duration via ffprobe? Use moviepy later, but estimate from file
    # Create ambient for this duration (use estimate + 2)
    # We'll get actual duration after loading wav
    sr_wav, data = wavfile.read(out_wav)
    if data.ndim > 1:
        data = data.mean(axis=1)
    duration = len(data) / sr_wav
    total_dur += duration
    print(f"Voice {i} duration {duration:.2f}s")

    # Generate immersive ASMR ambient for this scene
    ambient = make_ambient(i, duration + 0.5)
    # Make stereo ambient for binaural immersion: left/right slightly different
    ambient_l = ambient + brown_noise(len(ambient), 0.02, seed=i*100+1) * 0.3
    ambient_r = ambient + brown_noise(len(ambient), 0.02, seed=i*100+2) * 0.3
    # Normalize stereo
    ambient_stereo = np.stack([ambient_l, ambient_r], axis=1)
    ambient_stereo = ambient_stereo / (np.max(np.abs(ambient_stereo)) + 1e-6) * 0.18

    # Save ambient stereo wav
    ambient_path = f"output/ambient_v6_{i}.wav"
    # Convert to int16 stereo
    ambient_int = (ambient_stereo * 32767).astype(np.int16)
    wavfile.write(ambient_path, sr, ambient_int)

    # Mix voice + ambient (voice mono to stereo)
    # Voice data is mono, convert to stereo
    if data.dtype == np.int16:
        voice_float = data.astype(np.float32) / 32767.0
    else:
        voice_float = data.astype(np.float32) / np.max(np.abs(data))
    voice_stereo = np.stack([voice_float, voice_float], axis=1)
    # Trim ambient to voice length
    min_len = min(len(voice_stereo), len(ambient_stereo))
    mixed = voice_stereo[:min_len] * 0.92 + ambient_stereo[:min_len] * 0.35
    # Normalize
    mixed = mixed / (np.max(np.abs(mixed)) + 1e-6) * 0.85
    mixed_int = (mixed * 32767).astype(np.int16)
    mixed_path = f"output/v6_mixed_{i}.wav"
    wavfile.write(mixed_path, sr, mixed_int)

    # Create video segment with improved montage: slow zoom, vignette, grain, subtle movement
    seg_mp4 = f"output/v6_seg_{i}.mp4"
    # More cinematic: zoompan slow, eq brightness/contrast, vignette stronger, film grain
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "zoompan=z='if(lte(zoom,1.0),1.0,min(zoom+0.0006,1.18))':d=1:s=1920x1080:fps=24,"
        "eq=brightness=0.02:contrast=1.08:saturation=0.85,"
        "vignette=angle=PI/4:mode=forward,"
        "noise=alls=8:allf=t"
    )
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", images[i],
        "-i", mixed_path,
        "-vf", vf,
        "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv444p", "-r", "24",
        "-c:a", "aac", "-b:a", "128k", "-ac", "2",
        "-shortest",
        seg_mp4
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Segment {i} {duration:.2f}s ASMR immersive")
    processed.append(seg_mp4)

print(f"Total duration: {total_dur:.2f}s")

# Concatenate with xfade 1.8s for smooth ASMR transition
# Build xfade chain
current = processed[0]
for idx in range(1, len(processed)):
    next_seg = processed[idx]
    out = f"output/v6_xfade_{idx}.mp4"
    # get durations
    # Use ffprobe to get duration? Approximate via previous
    # For xfade we need offset = total previous - 1.8
    # We'll compute cumulative
    # Simplified: use 1.8s xfade
    # Need to get duration of current
    # Use ffprobe
    def get_dur(path):
        cmd = [FFMPEG.replace('ffmpeg','ffprobe'), "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
        # try imageio-ffprobe
        try:
            import imageio_ffmpeg
            ffprobe = imageio_ffmpeg.get_ffprobe_exe()
            cmd[0] = ffprobe
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            return durations_estimate[idx-1]
    try:
        import imageio_ffmpeg
        ffprobe = imageio_ffmpeg.get_ffprobe_exe()
        def get_duration(p):
            r = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", p], capture_output=True, text=True)
            return float(r.stdout.strip())
        dur_current = get_duration(current)
    except:
        dur_current = total_dur / len(processed)
    offset = max(0, dur_current - 1.8)
    cmd = [
        FFMPEG, "-y",
        "-i", current,
        "-i", next_seg,
        "-filter_complex",
        f"[0][1]xfade=transition=fade:duration=1.8:offset={offset},format=yuv444p[v];[0:a][1:a]acrossfade=d=1.8[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv444p",
        "-c:a", "aac", "-b:a", "128k", "-ac", "2",
        out
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    current = out
    print(f"Xfade {idx} offset {offset:.2f}")

# Final mix with subtle master ambient bed (very low brown + sub) for continuity
final_video = "output/V6_ASMR_IMMERSIVE_ARABIC.mp4"
# Create master ambient bed 2 sec longer than total
master_ambient = brown_noise(int((total_dur+2)*sr), 0.03, seed=999) + np.sin(2*np.pi*32*np.arange(int((total_dur+2)*sr))/sr)*0.01
master_path = "output/master_ambient_v6.wav"
wavfile.write(master_path, sr, (master_ambient*0.5*32767).astype(np.int16))

# Mix final audio with master bed for cohesion
final_mixed = "output/FINAL_V6_ASMR_IMMERSIVE.mp4"
cmd = [
    FFMPEG, "-y",
    "-i", current,
    "-i", master_path,
    "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 0.15[a]",
    "-map", "0:v", "-map", "[a]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ac", "2",
    final_mixed
]
subprocess.run(cmd, check=True)
print(f"Final ASMR Immersive: {final_mixed}")

# Cleanup intermediates
for f in os.listdir("output"):
    if f.startswith("v6_seg_") or f.startswith("v6_xfade_") or f.startswith("v6_mixed_") or f.startswith("ambient_v6_") or f.startswith("v6_asmr_voice_") or f.startswith("master_ambient"):
        os.remove(os.path.join("output", f))

print("Done V6 ASMR Immersive!")
