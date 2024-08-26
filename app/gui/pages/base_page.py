import customtkinter as ctk

class BasePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.canvas = ctk.CTkCanvas(self, width=1920, height=1080)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=master.bg_image, anchor="nw")
