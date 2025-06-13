import os
import subprocess
import streamlit as st
from deepgram import DeepgramClient, PrerecordedOptions
import yt_dlp  # ✅ Now using yt_dlp as a Python module instead of subprocess

# Your Deepgram API Key
DEEPGRAM_API_KEY = "c5266df73298444472067b2cdefda1b96a7c1589"
AUDIO_FILE = "downloaded_audio.wav"
TEMP_MP3 = "temp_raw_audio.mp3"

# Initialize Deepgram client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Transcribe audio using Deepgram
def transcribe(audio_path):
    options = PrerecordedOptions(
        model="nova-3",
        language="en",
        smart_format=True,
        punctuate=True,
        paragraphs=True,
    )

    with open(audio_path, "rb") as audio:
        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            audio, options, mimetype="audio/wav"
        )

    transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
    return transcript

# ✅ Download audio using yt-dlp (MP3) and convert to proper 16kHz WAV using ffmpeg
def download_audio(url):
    try:
        # Step 1: Download MP3
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": TEMP_MP3,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Step 2: Convert MP3 to Deepgram-friendly WAV (16000Hz, PCM)
        subprocess.run([
            "ffmpeg", "-y", "-i", TEMP_MP3,
            "-acodec", "pcm_s16le", "-ar", "16000", AUDIO_FILE
        ], check=True)

        return AUDIO_FILE

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg conversion failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Audio download/process failed: {e}")

# Streamlit app UI
st.title("🎬 Paste Video Link to Transcribe")
st.write("Paste any public video link (YouTube, TikTok, etc.), and get an AI transcript using Deepgram Nova-3.")

video_url = st.text_input("📎 Paste public video link here:")

if st.button("Start Transcription"):
    if not video_url.strip():
        st.warning("Please enter a valid video link.")
    else:
        with st.spinner("🔽 Downloading audio..."):
            try:
                audio_path = download_audio(video_url)
            except Exception as e:
                st.error(f"❌ Failed to download audio: {e}")
                audio_path = None

        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path)

            with st.spinner("💬 Transcribing..."):
                try:
                    transcript = transcribe(audio_path)
                    st.success("✅ Transcription complete!")
                    st.subheader("📄 Transcript")
                    st.text_area("Transcript", transcript, height=300)
                    st.download_button("📥 Download Transcript (.txt)", data=transcript, file_name="transcript.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"❌ Transcription failed: {e}")

            # Clean up temp files
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(TEMP_MP3):
                os.remove(TEMP_MP3)
