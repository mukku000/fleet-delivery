import os
import glob
import asyncio
import numpy as np
import scipy.io.wavfile as wavfile
import edge_tts
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip

RECORD_DIR = "/config/Desktop/Session1/fleet-delivery-agent/demo_recordings"
OUTPUT_VIDEO = "/config/Desktop/Session1/fleet-delivery-agent/demo_agent.mp4"
ARTIFACT_VIDEO = "/config/.gemini/antigravity/brain/5371dd96-2d10-40cb-98cf-06aa057924e9/demo_agent.mp4"
VOICEOVER_WAV = "/tmp/voiceover.mp3"
LOFI_WAV = "/tmp/lofi_music.wav"

VOICEOVER_TEXT = (
    "Welcome to NovaSmart Fleet Delivery Ops, an intelligent enterprise agent built for high-velocity dark-store delivery, "
    "rider routing, and package tracking. "
    "First, we check express order ORD-101. The agent queries Firestore and renders a rich A2UI card with order status, "
    "courier details, and interactive action buttons. "
    "Next, we click Route Weather. The agent fetches real-time route weather and safety alerts from the National Weather Service API. "
    "Finally, we request a live route map and an item promo video. Using Google Maps Static API and Google's Omni model gemini-omni-flash-preview, "
    "the agent generates a visual route map and an AI promo video uploaded to public Cloud Storage. "
    "Experience the future of intelligent fleet management with NovaSmart AI!"
)

async def generate_voiceover():
    print("1. Generating voiceover narration using edge-tts...")
    communicate = edge_tts.Communicate(VOICEOVER_TEXT, voice="en-US-AvaNeural")
    await communicate.save(VOICEOVER_WAV)
    print("Voiceover saved to:", VOICEOVER_WAV)

def generate_lofi_music(duration_sec=42, sample_rate=44100):
    print(f"2. Synthesizing upbeat lo-fi background music track ({duration_sec}s)...")
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)
    
    # Lo-fi chord progression: Cmaj7 - Am7 - Fmaj7 - G7
    # Frequencies: C4=261.63, E4=329.63, G4=392.00, B4=493.88
    # Am7: A3=220.00, C4=261.63, E4=329.63, G4=392.00
    # Fmaj7: F3=174.61, A3=220.00, C4=261.63, E4=329.63
    # G7: G3=196.00, B3=246.94, D4=293.66, F4=349.23
    
    chord_duration = 2.0  # seconds per chord
    num_chords = int(duration_sec / chord_duration) + 1
    
    music = np.zeros_like(t)
    
    chord_freqs = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [220.00, 261.63, 329.63, 392.00],  # Am7
        [174.61, 220.00, 261.63, 329.63],  # Fmaj7
        [196.00, 246.94, 293.66, 349.23],  # G7
    ]
    
    for i in range(num_chords):
        start_idx = int(i * chord_duration * sample_rate)
        end_idx = int((i + 1) * chord_duration * sample_rate)
        if start_idx >= len(t):
            break
        end_idx = min(end_idx, len(t))
        t_chunk = t[start_idx:end_idx] - t[start_idx]
        
        freqs = chord_freqs[i % len(chord_freqs)]
        chord_wave = np.zeros_like(t_chunk)
        for f in freqs:
            # Soft Rhodes-style synth wave with low-pass harmonics
            chord_wave += 0.25 * np.sin(2 * np.pi * f * t_chunk)
            chord_wave += 0.10 * np.sin(2 * np.pi * (f * 2) * t_chunk)
        
        # Envelope for smooth lo-fi swell
        env = np.sin(np.pi * t_chunk / chord_duration) ** 0.5
        music[start_idx:end_idx] += chord_wave * env
    
    # Add a gentle lo-fi drum beat (kick on beat 1 & 3, snare/hihat on 2 & 4)
    beat_sec = 0.5  # 120 bpm
    num_beats = int(duration_sec / beat_sec)
    beat_wave = np.zeros_like(t)
    for b in range(num_beats):
        b_start = int(b * beat_sec * sample_rate)
        b_len = int(0.1 * sample_rate)
        if b_start + b_len < len(beat_wave):
            t_beat = np.linspace(0, 0.1, b_len, False)
            if b % 2 == 0:
                # Muted lo-fi kick drum (pitch drop)
                kick = np.sin(2 * np.pi * 60 * np.exp(-30 * t_beat) * t_beat) * np.exp(-15 * t_beat)
                beat_wave[b_start:b_start+b_len] += 0.3 * kick
            else:
                # Soft lo-fi snare / rimshot noise
                snare = (np.random.rand(b_len) * 2 - 1) * np.exp(-25 * t_beat)
                beat_wave[b_start:b_start+b_len] += 0.15 * snare
    
    # Add subtle vinyl crackle
    crackle = (np.random.rand(len(t)) * 2 - 1) * 0.015
    
    final_music = (music * 0.6) + beat_wave + crackle
    final_music = final_music / np.max(np.abs(final_music)) * 0.25  # Normalised low background volume
    
    audio_int16 = (final_music * 32767).astype(np.int16)
    wavfile.write(LOFI_WAV, sample_rate, audio_int16)
    print("Lo-fi music saved to:", LOFI_WAV)

def compose_final_video():
    print("3. Composing final video with MoviePy...")
    webm_files = glob.glob(os.path.join(RECORD_DIR, "*.webm"))
    if not webm_files:
        raise RuntimeError("No raw webm video recordings found!")
    
    raw_video_file = webm_files[0]
    print("Using raw webm file:", raw_video_file)

    video_clip = VideoFileClip(raw_video_file)
    voice_clip = AudioFileClip(VOICEOVER_WAV)
    lofi_clip = AudioFileClip(LOFI_WAV)

    # Set video duration to match voiceover + trailing pad (e.g. max(video.duration, voice.duration + 2))
    target_duration = max(video_clip.duration, voice_clip.duration + 2)
    if video_clip.duration < target_duration:
        # Loop or hold final frame
        video_clip = video_clip.with_duration(target_duration)

    lofi_clip = lofi_clip.with_duration(target_duration)

    # Combine voiceover (full volume) and lo-fi background music
    composite_audio = CompositeAudioClip([
        lofi_clip.with_volume_scaled(0.3),
        voice_clip.with_volume_scaled(1.0)
    ])

    final_clip = video_clip.with_audio(composite_audio)
    
    print("Writing final demo video MP4 to:", OUTPUT_VIDEO)
    final_clip.write_videofile(
        OUTPUT_VIDEO,
        codec="libx264",
        audio_codec="aac",
        fps=24,
        logger=None
    )
    
    # Copy to artifacts directory
    os.makedirs(os.path.dirname(ARTIFACT_VIDEO), exist_ok=True)
    final_clip.write_videofile(
        ARTIFACT_VIDEO,
        codec="libx264",
        audio_codec="aac",
        fps=24,
        logger=None
    )

    print("Success! Demo video generated at:")
    print("  Local:", OUTPUT_VIDEO)
    print("  Artifact:", ARTIFACT_VIDEO)

async def main():
    await generate_voiceover()
    
    # Get voiceover length
    voice_audio = AudioFileClip(VOICEOVER_WAV)
    duration = max(40, voice_audio.duration + 4)
    voice_audio.close()

    generate_lofi_music(duration_sec=duration)
    compose_final_video()

if __name__ == "__main__":
    asyncio.run(main())
