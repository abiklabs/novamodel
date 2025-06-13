import os
import subprocess
import streamlit as st
from deepgram import DeepgramClient, PrerecordedOptions
import yt_dlp  # 👈 use the module like your working code

# Your Deepgram API Key (leave hardcoded during dev)
DEEPGRAM_API_KEY = "c5266df73298444472067b2cdefda1b96a7c1589"

# File paths
TEMP_MP3 = "/tmp/audio_temp.mp3"
AUDIO_FILE = "/tmp/audio_converted.wav"

# Initialize Deepgram client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# -----------------------------
# Transcribe audio using Deepgram Nova-3
# -----------------------------
def transcribe(audio_path):
    options = PrerecordedOptions(
        model="nova-3",
        language="en",
        smart_format=True,
        punctuate=True,
        paragraphs=True,
    )

    with open(audio_path, "rb") as audio_file:
        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            audio_file, options, mimetype="audio/wav"
        )

    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

# -----------------------------
# Download + Convert Audio (yt-dlp → mp3 → 16kHz .wav)
# -----------------------------
def download_audio(url):
    try:
        output_path = TEMP_MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        # Download using yt-dlp (like your working version)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(output_path):
            raise RuntimeError("yt-dlp failed to extract usable audio.")

        # Convert mp3 → WAV (Deepgram-safe: 16kHz, PCM)
        subprocess.run([
            "ffmpeg", "-y", "-i", output_path,
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            AUDIO_FILE
        ], check=True)

        return AUDIO_FILE

    except Exception as e:
        raise RuntimeError(f"❌ Audio download or conversion failed: {e}")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎬 Paste Video Link to Transcribe")
st.write("Paste any public video URL (YouTube, TikTok, etc.) to generate an AI transcript using **Deepgram Nova-3**")

video_url = st.text_input("📎 Paste public video link here:")

if st.button("Start Transcription"):
    if not video_url.strip():
        st.warning("⚠️ Please enter a valid video link.")
    else:
        with st.spinner("🔽 Downloading and preparing audio..."):
            try:
                audio_path = download_audio(video_url)
            except Exception as e:
                st.error(str(e))
                audio_path = None

        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path)

            with st.spinner("💬 Transcribing with Deepgram Nova-3..."):
                try:
                    transcript = transcribe(audio_path)
                    st.success("✅ Transcription Complete!")
                    st.subheader("📄 Transcript")
                    st.text_area("Transcript", transcript, height=300)
                    st.download_button("📥 Download Transcript", data=transcript, file_name="transcript.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"❌ Transcription failed: {e}")

            # Clean up temp files
            try:
                if os.path.exists(TEMP_MP3):
                    os.remove(TEMP_MP3)
                if os.path.exists(AUDIO_FILE):
                    os.remove(AUDIO_FILE)
            except:
                pass
