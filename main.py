import streamlit as st
import nest_asyncio
import yt_dlp
import asyncio
from deepgram import Deepgram
import os

# Setup asyncio for Streamlit
nest_asyncio.apply()

# Load API Key
DEEPGRAM_API_KEY = "c5266df73298444472067b2cdefda1b96a7c1589"

# Clean layout config
st.set_page_config(page_title="Transcribe", layout="centered")

# ----------------------------
# UI - Clean Tabbed Layout
# ----------------------------

st.title("🎙️ Transcribe Audio or Video to Text")

tab_upload, tab_link = st.tabs(["Upload", "From link"])

uploaded_file = None
video_url = ""

with tab_upload:
    st.markdown("### Upload a file")
    uploaded_file = st.file_uploader("Choose a file (MP3 or MP4)", type=["mp3", "mp4"])

with tab_link:
    st.markdown("### Paste video or audio link")
    video_url = st.text_input("Enter your link here...", placeholder="e.g. https://youtube.com/...")


# ----------------------------
# Helpers
# ----------------------------

def save_uploaded_file(file):
    path = os.path.join("/tmp", file.name)
    with open(path, "wb") as f:
        f.write(file.read())
    return path

def download_audio(url):
    output_base = "/tmp/audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_base + '.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_base + ".mp3"

async def transcribe(mp3_path):
    dg = Deepgram(DEEPGRAM_API_KEY)
    with open(mp3_path, 'rb') as f:
        source = {'buffer': f, 'mimetype': 'audio/mp3'}
        response = await dg.transcription.prerecorded(source, {
            "punctuate": True,
            "smart_format": True
        })
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

# ----------------------------
# Transcribe Trigger
# ----------------------------

if uploaded_file or video_url:
    if st.button("🧠 Transcribe"):
        audio_path = None

        if uploaded_file:
            with st.spinner("📦 Saving uploaded file..."):
                audio_path = save_uploaded_file(uploaded_file)

        elif video_url.strip():
            with st.spinner("🔗 Downloading from link..."):
                try:
                    audio_path = download_audio(video_url)
                except Exception as e:
                    st.error(f"❌ Failed to fetch audio: {e}")

        # Process transcript
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
