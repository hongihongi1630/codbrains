import customtkinter as ctk
import threading
import time

from app.gui.pages.base_page import BasePage

import app.chatbot.function as function

class ChatPage(BasePage):
    def __init__(self, master):
        super().__init__(master)

        self.response_label = ctk.CTkLabel(self, text="", font=("Helvetica", 30), wraplength=1000)
        self.response_label.place(relx=0.5, rely=0.5, anchor="center")

        self.recording_button = ctk.CTkButton(
            self,
            text="사랑이에게 추억 얘기하기",
            width=self.master.button_width,
            height=self.master.button_height,
            font=(self.master.font, self.master.font_size),
            fg_color=self.master.button_colors["fg_color"],
            hover_color=self.master.button_colors["hover_color"],
            text_color=self.master.button_colors["text_color"],
            command=self.start_recording)
        self.recording_button.place(relx=0.5, rely=0.9, anchor="center")

        self.create_button = ctk.CTkButton(
            self,
            text="동화 생성하기",
            width=self.master.button_width,
            height=self.master.button_height,
            font=(self.master.font, self.master.font_size),
            fg_color=self.master.button_colors["fg_color"],
            hover_color=self.master.button_colors["hover_color"],
            text_color=self.master.button_colors["text_color"],
            command=self.create_fairy_tail)

        self.my_text = ""
        self.response_cnt = 0
        self.is_recording_completed = False

        self.recording_thread = threading.Thread(target=self._start_recording)

    def initialize(self):
        self.my_text = ""
        self.is_recording_completed = False
        self.recording_button.configure(text="사랑이에게 추억 얘기하기", command=self.start_recording)
        self.recording_thread = threading.Thread(target=self._start_recording)
        # self.update()

    def start_recording(self):
        function.audio.play(self.master.project_dir + "/../assets/in.wav")
        print("Recording...")
        self.recording_thread.start()
        self.recording_button.configure(text="녹음 완료", command=self.finish_recording)

    def _start_recording(self):
        with function.speech_recognition.Microphone(
            device_index = None if function.audio_input_device_id == -2 else function.audio_input_device_id,
        ) as source:
            all_audio_data = function.io.BytesIO()

            while not self.is_recording_completed:
                try:
                    audio = function.recognizer.listen(source, timeout=1)
                    all_audio_data.write(audio.get_raw_data())
                except function.speech_recognition.WaitTimeoutError:
                    pass

            all_audio_data.seek(0)
            audio_data = function.speech_recognition.AudioData(
                all_audio_data.read(),
                source.SAMPLE_RATE,
                source.SAMPLE_WIDTH,
            )

            try:
                self.my_text = function.recognizer.recognize_google(audio_data, language=function.LANGUAGE_CODE + "-" + function.COUNTRY_CODE)
                print("You said: ", self.my_text)
            except function.speech_recognition.UnknownValueError or function.speech_recognition.RequestError:
                self.my_text = ""

    def finish_recording(self):
        function.audio.play(self.master.project_dir + "/../assets/out.wav")
        self.is_recording_completed = True
        while self.my_text == "":
            pass
        answer = self.master.pilot_gpt.chat(self.my_text)
        # self.recording_thread.join()
        self.show_response(answer)


    def show_response(self, answer):
        self.response_cnt += 1
        print("Answer: ", answer)

        self.response_label.configure(text="")

        self.master.speak_thread = threading.Thread(target=self.master.speak_tts, daemon=True).start()
        self.master.speak_text = answer
        while not self.master.speak_ready: # wait until the response is ready
            pass

        for char in answer:
            self.response_label.configure(text=self.response_label.cget("text") + char)
            self.update()
            time.sleep(self.master.text_speed_normal)
            if char == "." or char == "!" or char == "?" or char == ",":
                time.sleep(self.master.text_speed_break)

        if self.response_cnt > self.master.max_response_cnt:
            text = "\n\n또는 이제 동화를 만들고 싶다면 아래 버튼을 눌러주세요."

            self.master.speak_text = ""
            self.master.speak_thread = threading.Thread(target=self.master.speak_tts, daemon=True).start()
            self.master.speak_text = text
            while not self.master.speak_ready: # wait until the response is ready
                pass

            for char in text:
                self.response_label.configure(text=self.response_label.cget("text") + char)
                self.update()
                time.sleep(self.master.text_speed_normal)
                if char == "." or char == "!" or char == "?" or char == ",":
                    time.sleep(self.master.text_speed_break)

            self.create_button.place(relx=0.5, rely=0.75, anchor="center")

        self.initialize()

    def create_fairy_tail(self):
        self.create_button.configure(text="동화 생성 중...", state="disabled")
        create_prompt = "지금까지의 추억정보를 바탕으로 감동적인 장문의 동화를 생성해줘. 그리고 동화를 크게 5개의 구절로 쪼개주고 각 구절 마다 5문장으로 구성하면 돼. 구절 사이에 '//'를 넣어줘. 딱 결과만 출력해줘."
        answer = self.master.pilot_gpt.chat(create_prompt)
        self.master.show_page("result", answer)
