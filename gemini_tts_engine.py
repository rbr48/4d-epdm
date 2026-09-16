#!/usr/bin/env python3
"""
Gemini Female Neural TTS Engine for Izhaan Intellect
====================================================
Generates natural, breathing, expressive documentary voiceover
using Gemini TTS (gemini-3.1-flash-tts-preview) with key rotation
across user-provided API keys.
"""

import os
import sys
import wave
import time
import subprocess
from pathlib import Path
from typing import Optional, List
from google import genai
from google.genai import types

import json

ROOT = Path(__file__).resolve().parent

def load_gemini_keys() -> List[str]:
    """Load keys from .gemini_keys.json, .env, or system environment variables."""
    keys = []
    # 1. Try .gemini_keys.json
    keys_file = ROOT / ".gemini_keys.json"
    if keys_file.exists():
        try:
            with open(keys_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    keys.extend([k.strip() for k in loaded if isinstance(k, str) and k.strip()])
        except Exception:
            pass
    
    # 2. Try env variables
    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env_key and env_key not in keys:
        keys.append(env_key)
        
    return keys

GEMINI_KEYS: List[str] = load_gemini_keys()

_current_key_idx = 0

def get_next_key() -> str:
    global _current_key_idx
    if not GEMINI_KEYS:
        return ""
    k = GEMINI_KEYS[_current_key_idx % len(GEMINI_KEYS)]
    _current_key_idx += 1
    return k

def save_raw_pcm_to_wav(pcm_bytes: bytes, out_wav_path: Path, sample_rate: int = 24000) -> None:
    """Save mono 16-bit PCM bytes to standard WAV file."""
    with wave.open(str(out_wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)

def convert_to_broadcast_wav(in_wav: Path, out_wav: Path) -> Path:
    """Convert mono 24kHz audio to broadcast 48kHz stereo WAV with subtle studio enhancement."""
    af = (
        "aresample=48000,"
        "pan=stereo|c0=c0|c1=c0,"
        "equalizer=f=220:t=q:w=1.2:g=1.5,"
        "equalizer=f=3400:t=q:w=1.5:g=1.8,"
        "acompressor=threshold=0.15:ratio=3.0:attack=15:release=120,"
        "loudnorm=I=-16:TP=-1.5:LRA=9"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_wav),
        "-af", af,
        "-c:a", "pcm_s16le",
        str(out_wav)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_wav

def get_media_duration(file_path: Path) -> float:
    """Probe exact duration of any media file in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def synthesize_gemini_voice(
    text: str,
    out_wav_path: Path,
    voice_name: str = "Aoede",
    style_prompt: str = (
        "Say in an exciting, highly natural, and authoritative documentary tone, "
        "with natural breathing pauses and dramatic emphasis:"
    ),
    max_retries: int = 5
) -> Path:
    """
    Synthesizes narration text using Gemini TTS API.
    Features key rotation and exponential backoff for high reliability.
    """
    if out_wav_path.exists() and out_wav_path.stat().st_size > 5000:
        return out_wav_path

    out_wav_path.parent.mkdir(parents=True, exist_ok=True)
    temp_raw_wav = out_wav_path.with_suffix(".raw24k.wav")

    formatted_prompt = f"{style_prompt}\n\n\"{text.strip()}\""

    for attempt in range(max_retries):
        key = get_next_key()
        os.environ["GEMINI_API_KEY"] = key
        os.environ["GOOGLE_API_KEY"] = key
        try:
            client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=25.0))
            resp = client.models.generate_content(
                model="gemini-3.1-flash-tts-preview",
                contents=formatted_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    )
                )
            )

            if not resp.candidates or not resp.candidates[0].content.parts:
                raise ValueError("Empty response from Gemini TTS API")

            pcm_data = resp.candidates[0].content.parts[0].inline_data.data
            save_raw_pcm_to_wav(pcm_data, temp_raw_wav, sample_rate=24000)

            # Convert to 48kHz stereo broadcast audio
            convert_to_broadcast_wav(temp_raw_wav, out_wav_path)
            if temp_raw_wav.exists():
                temp_raw_wav.unlink()

            return out_wav_path

        except Exception as e:
            print(f"       [TTS Retry {attempt+1}/{max_retries}] Key error: {e}. Rotating key...", flush=True)
            time.sleep(1.0)
            if attempt == max_retries - 1:
                # Fallback to high quality edge-tts female voice if all keys exhaust
                print(f"       [!] Gemini TTS retry limit reached. Using neural female fallback (en-US-AvaNeural)...", flush=True)
                import edge_tts
                import asyncio
                communicate = edge_tts.Communicate(text, "en-US-AvaNeural")
                asyncio.run(communicate.save(str(temp_raw_wav)))
                convert_to_broadcast_wav(temp_raw_wav, out_wav_path)
                if temp_raw_wav.exists():
                    temp_raw_wav.unlink()
                return out_wav_path

    return out_wav_path

if __name__ == "__main__":
    test_out = ROOT / "test_gemini_voice.wav"
    t = "In 1946, Tokyo lay in pulverized ashes. But within twenty-five years, Japan engineered an industrial catch-up without historical precedent."
    print("Testing Gemini TTS synthesis...")
    p = synthesize_gemini_voice(t, test_out, voice_name="Aoede")
    print(f"Generated test voiceover: {p} ({p.stat().st_size} bytes)")
    if test_out.exists():
        test_out.unlink()
    print("Test completed successfully!")
