from gtts import gTTS
import os
import uuid

def text_to_audio(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    filename = f"audio_{uuid.uuid4().hex}.mp3"
    tts.save(filename)
    return filename
