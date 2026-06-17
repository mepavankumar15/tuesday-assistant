"""Text-to-speech utility using gTTS."""
import io
from gtts import gTTS


def text_to_audio_bytes(text: str, lang: str = "en") -> bytes:
    """Convert text to MP3 bytes for st.audio()."""
    # Strip markdown and keep it concise for speech
    clean = text.replace("*", "").replace("#", "").replace("`", "")
    tts = gTTS(text=clean[:500], lang=lang, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()
