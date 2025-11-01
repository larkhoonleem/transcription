import os
import warnings
import streamlit as st
import smtplib
from email.message import EmailMessage
from datetime import datetime
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv

# ------------------ Setup ------------------
load_dotenv()
warnings.filterwarnings("ignore")

GENERATION_MODEL = "gpt-4o"
API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_SENDER = "larkhoon.leem@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

client = OpenAI(api_key=API_KEY)

st.set_page_config(page_title="Voice Memo Transcriber", layout="centered")
st.title("🎙️ Voice Memo Transcriber")

# ------------------ Session State ------------------
if "transcription" not in st.session_state:
    st.session_state.transcription = ""

# ------------------ Email Sending Function ------------------
def send_transcription_email(receiver_email, transcription_text, audio_bytes, audio_filename):
    """Send the transcription and audio file to the provided email address."""
    try:
        msg = EmailMessage()
        msg["Subject"] = "Voice Memo Transcription"
        msg["From"] = EMAIL_SENDER
        msg["To"] = receiver_email

        email_body = f"""
Hi there,

Here is the transcription of your uploaded audio file.

Transcription:
------------------------------------------------------------
{transcription_text}
------------------------------------------------------------

Sent automatically by the Voice Memo Transcriber app.
        """

        msg.set_content(email_body)
        msg.add_attachment(audio_bytes, maintype="audio", subtype="mpeg", filename=audio_filename)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        st.success(f"📨 Transcription sent successfully to {receiver_email}!")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")

# ------------------ Transcription Function ------------------
def transcribe_audio(audio_bytes, filename):
    """Transcribe uploaded audio using OpenAI Whisper API."""
    try:
        with st.spinner("🎧 Transcribing your audio file..."):
            audio_file = BytesIO(audio_bytes)
            audio_file.name = filename
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcript.text
    except Exception as e:
        st.error(f"❌ Transcription error: {e}")
        return None

# ------------------ Upload UI ------------------
st.markdown("### 📁 Upload your voice memo file")
uploaded_audio = st.file_uploader(
    "Choose an audio file",
    type=["m4a", "mp3", "wav", "aac", "ogg"]
)

email_receiver = st.text_input("📧 Enter your email address to receive the transcription")

if uploaded_audio and email_receiver:
    if st.button("🚀 Transcribe and Send"):
        audio_bytes = uploaded_audio.read()
        filename = uploaded_audio.name

        transcription = transcribe_audio(audio_bytes, filename)
        if transcription:
            st.session_state.transcription = transcription
            st.markdown("### 📝 Transcription Result")
            st.write(transcription)

            send_transcription_email(email_receiver, transcription, audio_bytes, filename)
