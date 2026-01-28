import customtkinter
import json
import os
from ui.app import App
from database import init_db

def load_config():
    if not os.path.exists('config.json'):
        return {}
    with open('config.json', 'r') as f:
        return json.load(f)

def main():
    config = load_config()
    init_db()
    
    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    app = App(config)
    app.mainloop()

if __name__ == "__main__":
    main()
