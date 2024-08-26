import customtkinter as ctk
from PIL import Image, ImageTk
import time
import requests
import threading
from io import BytesIO

from app.gui.pages.base_page import BasePage

class ResultPage(BasePage):
    def __init__(self, master):
        super().__init__(master)

        self.current_page = 0
        self.story_pages = []  # This will be filled with story content
        self.prompt_pages = []
        self.images = []  # This will be filled with ImageTk.PhotoImage objects

        # Image placeholder
        self.image_label = ctk.CTkLabel(self, text="")
        self.image_label.place(relx=0.5, rely=0.35, anchor="center")

        # Text area
        self.text_label = ctk.CTkLabel(self, text="", font=("Helvetica", 30), wraplength=1200)
        self.text_label.place(relx=0.5, rely=0.8, anchor="center")

        # Previous button
        self.prev_button = ctk.CTkButton(
            self,
            text="이전 페이지",
            width=self.master.button_width / 2,
            height=self.master.button_height / 2,
            font=(self.master.font, self.master.font_size),
            fg_color=self.master.button_colors["fg_color"],
            hover_color=self.master.button_colors["hover_color"],
            text_color=self.master.button_colors["text_color"],
            command=self.prev_page)
        self.prev_button.place(relx=0.1, rely=0.95, anchor="center")
        self.prev_button.configure(state="disabled")  # Initially disabled

        # Next button
        self.next_button = ctk.CTkButton(
            self,
            text="다음 페이지",
            width=self.master.button_width / 2,
            height=self.master.button_height / 2,
            font=(self.master.font, self.master.font_size),
            fg_color=self.master.button_colors["fg_color"],
            hover_color=self.master.button_colors["hover_color"],
            text_color=self.master.button_colors["text_color"],
            command=self.next_page)
        self.next_button.place(relx=0.90, rely=0.95, anchor="center")
        self.next_button.configure(state="disabled")  # Initially disabled

    def set_story(self, story_text):
        # Set up fairy tale text
        self.story_pages = story_text.split('//')

        for i in range(len(self.story_pages)):
            if len(self.story_pages[i]) == 0:
                self.story_pages.pop(i)
            else:
                self.story_pages[i] = self.story_pages[i].replace('\n', '')
                # 맨 앞에 part 1, part 2, ...
                self.prompt_pages.append("part " + str(i + 1) + self.story_pages[i])

        # Set up images
        image_urls = []
        for i in range(len(self.story_pages)):
            image_url = self.master.pilot_gpt.create_image(self.story_pages[i], i + 1)
            image_urls.append(image_url)
            print(self.story_pages[i], image_url, end='\n\n')

        self.load_images(image_urls)

        self.current_page = 0
        self.update_page()

    def load_images(self, image_urls):
        def load_image(url):
            try:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                img = img.resize((800, 800), Image.LANCZOS)
                return ctk.CTkImage(light_image=img, dark_image=img, size=(800, 800))
            except Exception as e:
                print(f"Error loading image from {url}: {e}")
                return None

        for url in image_urls:
            img = load_image(url)
            if img:
                self.images.append(img)
            else:
                # Use a placeholder image if loading fails
                self.images.append(self.create_placeholder_image())

    def create_placeholder_image(self):
        img = Image.new('RGB', (800, 800), color='gray')
        return ctk.CTkImage(light_image=img, dark_image=img, size=(800, 800))

    def update_page(self):
        if 0 <= self.current_page < len(self.story_pages):
            # Update image
            if self.current_page < len(self.images):
                self.image_label.configure(image=self.images[self.current_page])
            else:
                self.image_label.configure(image=self.create_placeholder_image())

            # Update text
            self.text_label.configure(text="")

            self.master.speak_text = ""
            self.master.speak_thread = threading.Thread(target=self.master.speak_tts, daemon=True).start()
            self.master.speak_text = self.story_pages[self.current_page]
            while not self.master.speak_ready: # wait until the response is ready
                pass

            for char in self.story_pages[self.current_page]:
                self.text_label.configure(text=self.text_label.cget("text") + char)
                self.update()
                time.sleep(self.master.text_speed_normal)
                if char == "." or char == "!" or char == "?" or char == ",":
                    time.sleep(self.master.text_speed_break)

            # Enable/disable navigation buttons
            self.prev_button.configure(state="normal" if self.current_page > 0 else "disabled")
            self.next_button.configure(state="normal" if self.current_page < len(self.story_pages) - 1 else "disabled")
        else:
            # Story finished or invalid page
            self.text_label.configure(text="동화가 끝났습니다.")
            self.prev_button.configure(state="normal" if self.current_page > 0 else "disabled")
            self.next_button.configure(state="disabled")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()

    def next_page(self):
        self.current_page += 1
        self.update_page()

    def reset(self):
        self.current_page = 0
        self.story_pages = []
        self.text_label.configure(text="")
        self.image_label.configure(image="")
        self.next_button.configure(state="disabled")