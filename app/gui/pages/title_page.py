import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time

import app.chatbot.function as function
from app.gui.pages.base_page import BasePage

class TitlePage(BasePage):
    def __init__(self, master):
        super().__init__(master)

        # 좌측 중앙 - 이미지1
        sarang_img = Image.open(
            self.master.project_dir + "/../assets/sarang.png"
        )
        sarang_img = sarang_img.resize((600, 600), Image.LANCZOS)  # 이미지 크기 조정
        self.sarang_img_tk = ImageTk.PhotoImage(sarang_img)
        # self.canvas.create_image(480, 380, image=self.sarang_img_tk, anchor="center")

        # 우측 상단 - 버튼
        self.setting_button = ctk.CTkButton(
            self,
            text="사랑이와 인사하기",
            width=self.master.button_width,
            height=self.master.button_height,
            font=(self.master.font, self.master.font_size),
            fg_color=self.master.button_colors["fg_color"],
            hover_color=self.master.button_colors["hover_color"],
            text_color=self.master.button_colors["text_color"],
            command=self.func_greeting)
        self.setting_button.place(relx=0.75, rely=0.25, anchor="center")

        # 우측 중앙 - 버튼
        self.chat_button = ctk.CTkButton(
            self,
            text="사랑이와 추억 회상하기",
            width=self.master.button_width,
            height=self.master.button_height,
            font=(self.master.font, self.master.font_size),
            fg_color=self.master.button_colors["fg_color"],
            hover_color=self.master.button_colors["hover_color"],
            text_color=self.master.button_colors["text_color"],
            command=self.go_to_chat)
        self.chat_button.place(relx=0.75, rely=0.50, anchor="center")

        # 우측 하단 - 버튼
        self.exit_button = ctk.CTkButton(
            self,
            text="종료하기",
            width=self.master.button_width,
            height=self.master.button_height,
            font=(self.master.font, self.master.font_size),
            fg_color=self.master.button_colors["fg_color"],
            hover_color=self.master.button_colors["hover_color"],
            text_color=self.master.button_colors["text_color"],
            command=self.master.destroy)
        self.exit_button.place(relx=0.75, rely=0.75, anchor="center")

        # 응답 텍스트
        self.response_label = ctk.CTkLabel(self, text="", font=(self.master.font, 30), wraplength=600)
        self.response_label.place(relx=0.25, rely=0.7, anchor="center")

        self.func_greeting_thread = threading.Thread(target=self._func_greeting, daemon=True)

    def func_greeting(self):
        self.setting_button.configure(state="disabled")
        self.func_greeting_thread.start()
        # self.func_greeting_thread.join()

    def _func_greeting(self):
        response = self.master.query_pilot_gpt("안녕 사랑아, 너에 대해서 알려줘.")
        self.display_response(response)

    def display_response(self, response):
        self.response_label.configure(text="")
        self.master.speak_text = response

        self.master.speak_thread.start()
        self.master.speak_text = response
        while not self.master.speak_ready: # wait until the response is ready
            pass

        for char in response:
            self.response_label.configure(text=self.response_label.cget("text") + char)
            self.update()
            time.sleep(self.master.text_speed_normal)
            if char == "." or char == "!" or char == "?" or char == ",":
                time.sleep(self.master.text_speed_break)

    def play_boot_sound(self):
        threading.Thread(target=self._play_boot_sound, daemon=True).start()

    def _play_boot_sound(self):
        function.audio.play(self.master.project_dir + "/../assets/boot.wav")

    def go_to_chat(self):
        self.master.show_page("chat")