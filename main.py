import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
from googletrans import Translator

import time
import random
import sys



RECORD_SECONDS = 5
SAMPLE_RATE = 44100
max_attempts = 3 
words = {
    "easy": ["кот", "собака", "яблоко", "молоко", "солнце"],
    "medium": ["банан", "школа", "друг", "окно", "жёлтый"],
    "hard": ["технология", "университет", "информация", "произношение", "воображение"]
}


def trans_recording(lang):
    duration = RECORD_SECONDS  # секунды записи
    sample_rate = SAMPLE_RATE
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
    try:
        text = recognizer.recognize_google(audio, language=lang)
    except sr.UnknownValueError:       
        text = "Не удалось распознать речь."
    except sr.RequestError as e:           
        text = f"Ошибка сервиса: {e}"

    if text in ("Не удалось распознать речь.",):
        return None
    return text

def translate_text(text, dest_lang="en"):
    try:
        translator = Translator()
        translated = translator.translate(text, dest=dest_lang)
        return translated.text
    except Exception:
        return None
    
def print_header():
    print("""
Привет! Давай поиграем в угадай слово!
Правила игры:
Выберите уровень сложности: easy / medium / hard.
Вам дадут слово выбранной сложности — скажите его вслух.
У вас есть 3 попытки на слово; после неудачи — game over.
""")
    
def choose_difficulty():
    while True:
        d = input("Выберите уровень (easy/medium/hard) [easy]: ").strip().lower()
        if d == "":
            return "easy"
        if d in words:
            return d
        print("Неверный уровень. Введите easy, medium или hard.")


def evaluate_guess(target, recognized):
    if not recognized:
        return 0, "Не распознано"
    if target.lower() == recognized.lower():
        return 10, f"Правильно!: '{recognized}'"
    return 0, f"Неверно:'{recognized}'"

def play_round(target_word, lang_display="ru-RU"):
    attempts_left = max_attempts
    while attempts_left > 0:
        input(f"Нажмите Enter, чтобы начать запись (осталось попыток: {attempts_left})...")
        recognized = trans_recording(lang_display)
        score, message = evaluate_guess(target_word, recognized)
        print("→", message)
        if score > 0:
            return score, True
        attempts_left -= 1
        if attempts_left > 0:
            print(f"Осталось попыток: {attempts_left}")

    print("GAME OVER!!!")
    return 0, False

def creativity_bonus(rounds_played):
    return (rounds_played // 3) * 5

def logic():
    print_header()
    difficulty = choose_difficulty()
    level_words = words[difficulty].copy()
    random.shuffle(level_words)
    total_score = 0
    rounds_played = 0
    successful_rounds = 0
    consecutive_fails = 0

    print(f"\nВыбрано: {difficulty}. Начинаем! (Количество попыток:{max_attempts})")
    for target in level_words:
        rounds_played += 1
        print(f"Слово для произнесения:{target.upper()}")
        gained, success = play_round(target, lang_display="ru-RU")
        if success:
            print(f"+{gained} баллов")
            total_score += gained
            successful_rounds += 1
            consecutive_fails = 0
        else:
            print("Вы ошиблись.")
            consecutive_fails += 1
        time.sleep(0.8)
        if consecutive_fails >= 3:
            print("Три неудачи подряд — игра окончена.")
            break
    bonus = creativity_bonus(successful_rounds)
    total_score += bonus

    print(f"Набрано очков: {total_score}")
    print(f"Отдельный бонус: {bonus}")
logic()