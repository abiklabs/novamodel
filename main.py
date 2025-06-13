import streamlit as st
from deepgram import DeepgramClient, PrerecordedOptions
import json

# Your Deepgram API key
DEEPGRAM_API_KEY = "c5266df73298444472067b2cdefda1b96a7c1589"

# Initialize Deepgram client
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Streamlit app starts here
def main():
    st.set_page_config(page_title="🎙️ Audio Transcriber", layout="centered")

    st.title("🎧 Deepgram Audio Transcriber")
    st.write("Paste a valid audio URL below and get the transcription using Deepgram Nova-3")

    # Input field for audio URL
    audio_url = st.text_input(
        "🔗 Audio File URL:",
        placeholder="https://example.com/audio.wav"
    )

    if st.button("🚀 Transcribe"):
        if not audio_url:
            st.error("Please enter a valid audio URL before clicking transcribe.")
            return

        with st.spinner("Transcribing... please wait ⏳"):
            try:
                options = PrerecordedOptions(
                    model="nova-3",
                    language="en",
                    smart_format=True,
                    punctuate=True,
                    paragraphs=True,
                )

                response = deepgram.listen.prerecorded.v("1").transcribe_url(
                    {"url": audio_url},
                    options,
                )

                # Parse and display result
                transcription = response["results"]["channels"][0]["alternatives"][0]["transcript"]

                st.success("✅ Transcription Complete!")
                st.subheader("📝 Transcript:")
                st.write(transcription)

                with st.expander("📄 Full JSON Response"):
                    st.json(response.to_dict())

            except Exception as e:
                st.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
