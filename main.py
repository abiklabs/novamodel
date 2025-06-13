import os
import subprocess
import asyncio
import streamlit as st
from deepgram import DeepgramClient, PrerecordedOptions

# Your Deepgram API key
DEEPGRAM_API_KEY = "c5266df73298444472067b2cdefda1b96a7c1589"
AUDIO_FILE = "downloaded_audio.wav"

# Initialize Deepgram client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Async transcription function
async def transcribe(audio_path):
    options = PrerecordedOptions(
        model="nova-3",
        language="en",
        smart_format=True,
        punctuate=True,
        paragraphs=True,
    )

    with open(audio_path, "rb") as audio:
        response = await deepgram.listen.prerecorded.v("1").transcribe_file_async(audio, options)

    transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
    return transcript

# Audio downloader using yt-dlp
def download_audio(url):
    try:
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "wav",
            "-o", AUDIO_FILE,
            url
        ], check=True)
        return AUDIO_FILE
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio download failed: {e}")

# Streamlit UI
st.title("🎬 Paste Video Link to Transcribe")

video_url = st.text_input("Paste public video link here (YouTube, TikTok, etc.)")

if st.button("Start Transcription"):
    if not video_url.strip():
        st.warning("Please paste a valid video link.")
    else:
        with st.spinner("🔽 Downloading audio..."):
            try:
                audio_path = download_audio(video_url)
            except Exception as e:
                st.error(f"❌ Failed to download audio: {e}")
                audio_path = None

        if audio_path:
            st.audio(audio_path)
            with st.spinner("💬 Transcribing..."):
                try:
                    transcript = asyncio.run(transcribe(audio_path))
                    st.success("✅ Done!")
                    st.subheader("📄 Transcript")
                    st.text_area("Transcript", transcript, height=300)
                    st.download_button("📥 Download Transcript (.txt)", data=transcript, file_name="transcript.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"❌ Transcription failed: {e}")
            os.remove(audio_path)
