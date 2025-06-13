import streamlit as st
import nest_asyncio
import yt_dlp
import asyncio
from deepgram import DeepgramClient, PrerecordedOptions
import os

# Setup asyncio for Streamlit
nest_asyncio.apply()

# For quick testing - API Key
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

def transcribe_file(file_path):
    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        
        # Configure transcription options with enhanced formatting
        options = PrerecordedOptions(
            model="nova-3",
            language="en",
            smart_format=True,
            punctuate=True,
            paragraphs=True,
            diarize=False,
            utterances=False,
            profanity_filter=False,
            filler_words=False,
            tier="enhanced"
        )
        
        # Read the file
        with open(file_path, 'rb') as audio:
            # Create the source object correctly
            source = {
                'buffer': audio,
                'mimetype': 'audio/mp3'  # or appropriate mimetype
            }
            
            # Transcribe the file
            response = deepgram.listen.prerecorded.v("1").transcribe_file(
                source,
                options
            )
            
            # Extract transcript from response
            return response.results.channels[0].alternatives[0].transcript
            
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

def transcribe_url(url):
    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        
        # Configure transcription options with enhanced formatting
        options = PrerecordedOptions(
            model="nova-3",
            language="en",
            smart_format=True,
            punctuate=True,
            paragraphs=True,
            diarize=False,
            utterances=False,
            profanity_filter=False,
            filler_words=False,
            tier="enhanced"
        )
        
        # Create the source object correctly
        source = {
            'url': url
        }
        
        # Transcribe the URL
        response = deepgram.listen.prerecorded.v("1").transcribe_url(
            source,
            options
        )
        
        # Extract transcript from response
        return response.results.channels[0].alternatives[0].transcript
        
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

# ----------------------------
# Transcribe Trigger
# ----------------------------

if uploaded_file or video_url:
    if st.button("🧠 Transcribe"):
        try:
            if uploaded_file:
                with st.spinner("📦 Processing uploaded file..."):
                    # Save the uploaded file
                    audio_path = save_uploaded_file(uploaded_file)
                    # Show audio player
                    st.audio(uploaded_file, format='audio/mp3')
                    # Transcribe the file
                    transcript = transcribe_file(audio_path)
                    
            elif video_url.strip():
                with st.spinner(" Processing URL..."):
                    # For direct audio/video URLs, use transcribe_url
                    if video_url.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
                        # Show audio player for direct audio URLs
                        st.audio(video_url, format='audio/mp3')
                        transcript = transcribe_url(video_url)
                    else:
                        # For YouTube or other video platforms, download first
                        audio_path = download_audio(video_url)
                        # Show audio player for downloaded audio
                        st.audio(audio_path, format='audio/mp3')
                        transcript = transcribe_file(audio_path)
            
            # Display results
            st.success("✅ Done!")
            st.subheader("📄 Transcript")
            st.text_area("Transcript", transcript, height=300)
            st.download_button(
                "📥 Download Transcript (.txt)",
                data=transcript,
                file_name="transcript.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
