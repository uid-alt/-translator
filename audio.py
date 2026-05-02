import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
from googletrans import Translator


def trans_recording(lang):
    duration = 5  # секунды записи
    sample_rate = 44100
    print("Говори...")
    recording = sd.rec(
    int(duration * sample_rate), # длительность записи в сэмплах
    samplerate=sample_rate,      # частота дискретизации
    channels=1,                  # 1 — это моно
    dtype="int16")               # формат аудиоданных
    sd.wait()  # ждём завершения записи
    wav.write("output.wav", sample_rate, recording)
    print("Запись завершена, теперь распознаём...")
    recognizer = sr.Recognizer()
    with sr.AudioFile("output.wav") as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source)
    lang = input("Введите код языка для перевода (например, 'en' — английский, 'es' — испанский): ")
    try:
        text = recognizer.recognize_google(audio, language=lang)
    except sr.UnknownValueError:             # - если Google не понял речь (шум, молчание)
        text = "Не удалось распознать речь."
    except sr.RequestError as e:             # - если нет интернета или API недоступен
        text = f"Ошибка сервиса: {e}"
    return text

def translate(text, lang):
    translator = Translator()
    translated = translator.translate(text, dest=lang)
    return translated.text
