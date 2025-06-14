import streamlit as st
import nest_asyncio
import yt_dlp
from deepgram import DeepgramClient, PrerecordedOptions
import os
import json

# Setup asyncio for Streamlit
nest_asyncio.apply()

# For quick testing - API Key
DEEPGRAM_API_KEY = "e8af3f12650ff4398b021c245489f0d2fed19f62"

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
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        options = PrerecordedOptions(
            model="nova-3",
            language="multi",
            smart_format=True,
            punctuate=True,
            paragraphs=True
        )
        with open(file_path, 'rb') as audio:
            source = {
                'buffer': audio,
                'mimetype': 'audio/mp3'
            }
            response = deepgram.listen.prerecorded.v("1").transcribe_file(
                source,
                options
            )
            return response.to_json(indent=4)
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

def transcribe_url(url):
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        options = PrerecordedOptions(
            model="nova-3",
            language="multi",
            smart_format=True,
            punctuate=True,
            paragraphs=True
        )
        source = {
            'url': url
        }
        response = deepgram.listen.prerecorded.v("1").transcribe_url(
            source,
            options
        )
        return response.to_json(indent=4)
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
                    audio_path = save_uploaded_file(uploaded_file)
                    st.audio(uploaded_file, format='audio/mp3')
                    response_json = transcribe_file(audio_path)
            elif video_url.strip():
                with st.spinner("🔗 Processing URL..."):
                    if video_url.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
                        st.audio(video_url, format='audio/mp3')
                        response_json = transcribe_url(video_url)
                    else:
                        audio_path = download_audio(video_url)
                        st.audio(audio_path, format='audio/mp3')
                        response_json = transcribe_file(audio_path)

            st.success("✅ Done!")
            st.subheader("📄 Transcript")

            # Parse the JSON response to get the transcript with proper paragraphs
            response_data = json.loads(response_json)
            paragraphs = []
            try:
                para_data = response_data["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
                for para in para_data:
                    # Join all sentences in this paragraph
                    if "sentences" in para and para["sentences"]:
                        text = " ".join(sentence["text"] for sentence in para["sentences"])
                        paragraphs.append(text.strip())
                    elif "transcript" in para:
                        paragraphs.append(para["transcript"].strip())
            except (KeyError, IndexError, TypeError):
                # Fallback: use the flat transcript
                paragraphs = [response_data['results']['channels'][0]['alternatives'][0]['transcript']]

            formatted_transcript = "\n\n".join(paragraphs)

            st.text_area(
                "Transcript",
                formatted_transcript,
                height=300,
                help="Paragraphs are separated by blank lines."
            )

            st.download_button(
                "📥 Download Transcript (.txt)",
                data=formatted_transcript,
                file_name="transcript.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
