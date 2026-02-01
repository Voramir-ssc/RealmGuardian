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
    import locale
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE')
    except locale.Error:
        print("Warning: Locale de_DE not available. Using system default.")

    config = load_config()
    init_db()
    
    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    app = App(config)
    
    if not config:
        from tkinter import messagebox
        # Delay slightly to ensure main window is ready or just show safe box
        # Since App is CTk, we can use its after method potentially, but simple messagebox works before mainloop too mostly
        # but better to do it after app init
        print("WARN: Config not found or empty.")
        # We can't easily show a popup before mainloop starts rendering sometimes with CTk, 
        # but let's try or just print to console (which user sees if they ran from cmd as they did).
    
    app.mainloop()

if __name__ == "__main__":
    main()
