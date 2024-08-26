import customtkinter as ctk
from PIL import Image, ImageTk
import threading

import app.chatbot.function as function

from app.gui.pages.title_page import TitlePage
from app.gui.pages.chat_page import ChatPage
from app.gui.pages.result_page import ResultPage

class GUI(ctk.CTk):
    def __init__(self, project_dir):
        super().__init__()
        self.project_dir = project_dir

        self.button_width = 400
        self.button_height = 150

        self.font = "Helvetica"
        self.font_size = 40

        self.max_response_cnt = 2

        self.text_speed_normal = 0.03
        self.text_speed_break = 0.1

        # self.text_speed_normal = 0.1
        # self.text_speed_break = 0.6

        self.button_colors = {
            "fg_color": "#DAEEFD",  # Default button color
            "hover_color": "#C9E6FC",  # Color when mouse hovers over the button
            "text_color": "Black",  # Text color
            "disabled_color": "#CCCCCC"  # Color when button is disabled
        }

        self.title("Codbrain")
        self.geometry("1920x1080")

        self.bg_image = self.load_background(
            self.project_dir + "/../assets/background.png"
        )

        self.pilot_gpt = function.pilot_gpt

        self.pages = {}
        self.current_page = None

        self.speak_text = ""
        self.speak_ready = False

        self.speak_thread = threading.Thread(target=self.speak_tts, daemon=True)

        self.create_pages()
        self.show_page("title")

    def load_background(self, image_path):
        image = Image.open(image_path)
        window_width = self.winfo_screenwidth()
        window_height = self.winfo_screenheight()
        image = image.resize((window_width, window_height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def create_pages(self):
        self.pages["title"] = TitlePage(self)
        self.pages["chat"] = ChatPage(self)
        self.pages["result"] = ResultPage(self)

    def show_page(self, page_name, answer=None):
        if self.current_page:
            self.current_page.pack_forget()
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)
        if page_name == "title":
            self.current_page.play_boot_sound()
        if page_name == "result":
            self.current_page.set_story(answer)

    def query_pilot_gpt(self, prompt):
        return self.pilot_gpt.chat(prompt)

    def speak_tts(self):
        while self.speak_text == "":
            pass
        response_voice = function.tts.parse(self.speak_text, function.LANGUAGE_CODE)
        self.speak_ready = True
        future_voice = function.audio.play(response_voice)
        # future_voice.result()

        # reset
        self.speak_text = ""
        self.speak_ready = False
        self.speak_thread = None
