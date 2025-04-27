import io

import pyttsx3

engine = pyttsx3.init()

def ttsmp3(text):
# convert this text to speech
    text = "Python is a great programming language"
    engine.setProperty("rate", 150)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[2].id)
    engine.save_to_file(text, 'tts_out.mp3')
    engine.runAndWait()

