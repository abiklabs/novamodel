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
