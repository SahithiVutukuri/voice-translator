import whisper
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
import sys
import io

# -- Ensure terminal can print Unicode --
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LANGUAGES = {
    "english": "en", "french": "fr", "spanish": "es", "hindi": "hi",
    "telugu": "te", "tamil": "ta", "japanese": "ja", "korean": "ko",
    "chinese": "zh-cn", "arabic": "ar"
    # Extend as needed
}

def safe_print(text):
    try:
        print(text)
    except Exception:
        print(text.encode('utf-8', errors='replace').decode('utf-8'))

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_voice(prompt):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    speak(prompt)
    safe_print(prompt)
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        safe_print(f'You said: {text}')
        return text.strip().lower()
    except Exception as e:
        safe_print(f"Could not recognize. Try again. {e}")
        speak("Could not recognize. Try again.")
        return None

def transcribe_speech_whisper():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    safe_print("Now, please speak the sentence you want to translate.")
    speak("Now, please speak the sentence you want to translate.")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    with open("input.wav", "wb") as f:
        f.write(audio.get_wav_data())
    try:
        # Let Whisper auto-detect language
        model = whisper.load_model("tiny")
        result = model.transcribe("input.wav")
        safe_print(f"[Recognized] {result['text']}")
        return result['text']
    except Exception as e:
        safe_print(f"Transcription error: {e}")
        speak("Sorry, could not transcribe your speech.")
        return ""

def main():
    safe_print("Supported languages: " + ", ".join(list(LANGUAGES.keys())))
    while True:
        # Step 1: Ask for target language
        lang_text = None
        while not lang_text:
            lang_text = recognize_voice("Which language do you want to translate to?")
        target_code = LANGUAGES.get(lang_text.lower())
        if not target_code:
            speak("Language not supported. Try again.")
            continue

        # Step 2: Get input sentence (spoken)
        sentence = transcribe_speech_whisper()
        if not sentence or not sentence.strip():
            speak("Sorry, I did not catch your sentence. Try again.")
            continue

        # Step 3: Translate and speak result
        translator = Translator()
        try:
            translated = translator.translate(sentence, dest=target_code)
            safe_print(f"[Translation: {lang_text.capitalize()}] {translated.text}")
            speak(translated.text)
        except Exception as e:
            safe_print("Translation error: " + str(e))
            speak("Translation error. Try again.")

        # Step 4: Continue or stop
        answer = recognize_voice("Do you want to translate another sentence? Say Yes or No.")
        if answer and "no" in answer:
            speak("Goodbye!")
            break

if __name__ == "__main__":
    main()
