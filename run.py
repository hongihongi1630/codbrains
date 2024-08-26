#!/usr/bin/env python3
from app.gui.gui import GUI
from app.config import project_dir

def main():
    gui = GUI(project_dir)
    gui.mainloop()

if __name__ == "__main__":
    main()