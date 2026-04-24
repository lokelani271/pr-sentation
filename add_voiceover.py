"""
Generate edge-tts voiceover and merge with auraease_v3_simple.mp4
"""

import asyncio, subprocess, os, ssl
import edge_tts
import edge_tts.communicate as _etc

# Bypass self-signed proxy certificate in this sandboxed environment
_permissive_ssl = ssl.create_default_context()
_permissive_ssl.check_hostname = False
_permissive_ssl.verify_mode = ssl.CERT_NONE
_etc._SSL_CTX = _permissive_ssl

DIR   = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.join(DIR, "auraease_v3_simple.mp4")
AUDIO = os.path.join(DIR, "voiceover.mp3")
OUT   = os.path.join(DIR, "auraease_v3_audio.mp4")

VOICE  = "en-US-JennyNeural"   # warm, natural female voice
RATE   = "+5%"                  # slight speed-up so 12s script fits cleanly

# Narration timed to the 4 scenes (12 seconds total)
SCRIPT = (
    "Your back is killing you... after another eight-hour day.  "   # 0-3s
    "Meet AuraEase. Hot and cold therapy — in one discreet patch.  " # 3-6s
    "Twelve hours of relief. Drug-free. Just thirty-five dollars.  " # 6-9s
    "AuraEase. The smarter choice. Link in bio."                      # 9-12s
)

async def gen_audio():
    print("Generating voiceover with edge-tts …")
    com = edge_tts.Communicate(SCRIPT, VOICE, rate=RATE)
    await com.save(AUDIO)
    print(f"  Audio saved → {AUDIO}")

def merge():
    print("Merging audio + video with ffmpeg …")
    cmd = [
        "ffmpeg", "-y",
        "-i", VIDEO,
        "-i", AUDIO,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-t", "12",                  # clamp to video length
        OUT,
    ]
    subprocess.run(cmd, check=True)
    print(f"\n✔  Final video → {OUT}")

if __name__ == "__main__":
    asyncio.run(gen_audio())
    merge()
