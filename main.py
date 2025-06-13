import streamlit as st
from deepgram import DeepgramClient, PreRecordedOptions
import os

# Your Deepgram API Key
DEEPGRAM_API_KEY = "c5266df73298444472067b2cdefda1b96a7c1589"

# Init Deepgram SDK client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

def main():
    st.set_page_config(page_title="🎙️ Audio Upload Transcriber", layout="centered")
    st.title("📤 Upload Audio → 🎧 Get Transcript")

    st.markdown("Upload an audio file (`.mp3`, `.wav`, `.m4a`, etc.) for transcription using **Deepgram Nova-3**.")

    uploaded_file = st.file_uploader("🎵 Upload Audio File:", type=["mp3", "wav", "m4a", "aac"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")

        if st.button("🚀 Transcribe Now"):
            with st.spinner("Transcribing your audio... 🤖"):
                try:
                    # Convert uploaded file to bytes for Deepgram
                    audio_bytes = uploaded_file.read()

                    # Build options
                    options = PreRecordedOptions(
                        model="nova-3",
                        language="en",
                        smart_format=True,
                        punctuate=True,
                        paragraphs=True,
                    )

                    # Make request to Deepgram using file input
                    response = deepgram.listen.prerecorded.v("1").transcribe_file(
                        audio=audio_bytes,
                        options=options
                    )

                    transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]

                    st.success("✅ Transcription Complete!")
                    st.subheader("📝 Transcript:")
                    st.write(transcript if transcript else "No speech detected.")

                    with st.expander("📄 View Full JSON Response"):
                        st.json(response.to_dict())

                except Exception as e:
                    st.error(f"❌ Error: {e}")
    else:
        st.info("Please upload an audio file to get started.")

if __name__ == "__main__":
    main()
