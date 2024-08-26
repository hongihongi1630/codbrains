import json
import time
from typing import Final
import concurrent.futures
import pyaudio
import speech_recognition
import threading
import io

import app.chatbot.audio as audio
import app.chatbot.gpt as gpt
import app.chatbot.tts as tts
import app.chatbot.utils as utils

from app.config import project_dir

with open(project_dir + '/../configuration.json', 'r', encoding='utf-8') as file:
    env = json.load(file)

OPENAI_API_KEY: Final[str] = str(env.get('openai_api_key'))
OPENAI_GPT_MODEL: Final[str] = str(env.get('openai_gpt_model', 'gpt-4'))
OPENAI_GPT_INSTRUCTIONS: Final[str] = str(env.get('openai_gpt_instructions', ''))
LANGUAGE_CODE: Final[str] = str(env.get('language_code', 'en'))
COUNTRY_CODE: Final[str] = str(env.get('country_code', 'US'))

pilot_gpt = gpt.ChatGPT(
    key = OPENAI_API_KEY,
    default_model = OPENAI_GPT_MODEL,
    instructions = OPENAI_GPT_INSTRUCTIONS,
)
pyaudio = pyaudio.PyAudio()
recognizer = speech_recognition.Recognizer()

audio_input_device_id = int(env.get('audio_input_device_id'))
if audio_input_device_id == -1:
    audio.list_audio_input_devices(pyaudio)
    audio_input_device_id = int(input("Enter the ID of the audio input device you want to use: "))

def listen_voice_with_manual_control(recognizer, source, language):
    """
    Record voice input with manual start and stop control.
    """
    print("Press Enter to start recording...")
    input()
    print("Recording... Press Enter to stop.")

    stop_recording = threading.Event()
    all_audio_data = io.BytesIO()

    def wait_for_stop():
        input()
        stop_recording.set()

    stop_thread = threading.Thread(target=wait_for_stop)
    stop_thread.start()

    # Continue recording until user presses Enter
    while not stop_recording.is_set():
        try:
            audio = recognizer.listen(source, timeout=1)
            all_audio_data.write(audio.get_raw_data())
        except speech_recognition.WaitTimeoutError:
            pass

    print("Recording stopped.")

    # Create an AudioData object from the accumulated raw audio data
    all_audio_data.seek(0)
    audio_data = speech_recognition.AudioData(all_audio_data.read(), source.SAMPLE_RATE, source.SAMPLE_WIDTH)

    try:
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except speech_recognition.UnknownValueError:
        print("Sorry, I couldn't understand that.")
        return ""
    except speech_recognition.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def listen_to_user(source):
    """
    Records voice with manual control and converts it to text.
    """
    audio.play(project_dir + '/../assets/in.wav')
    question = listen_voice_with_manual_control(
        recognizer = recognizer,
        source = source,
        language = LANGUAGE_CODE + '-' + COUNTRY_CODE
    )
    audio.play(project_dir + '/../assets/out.wav')
    print("You said: ", question)
    return question

def respond_to_user(question):
    """
    Sends the question to ChatGPT and outputs the response as voice and text.
    """
    if not question:
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_loading_sound = executor.submit(
            audio.play,
            project_dir + '/../assets/loading.wav'
        )
        response_text = executor.submit(pilot_gpt.chat, question).result()
        response_voice = executor.submit(tts.parse, response_text, LANGUAGE_CODE).result()
        future_loading_sound.cancel()
        time.sleep(0.6)
        # future_print = executor.submit(utils.print_slowly, response_text)
        future_voice = executor.submit(audio.play, response_voice)
        # future_print.result()
        future_voice.result()

    return response_text