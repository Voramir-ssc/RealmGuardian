import customtkinter
from tkinter import messagebox
from database import get_session
from models.character import Character

class BarracksFrame(customtkinter.CTkFrame):
    def __init__(self, master, engine):
        super().__init__(master)
        self.engine = engine
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = customtkinter.CTkLabel(self, text="Kaserne - Charakterverwaltung", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Character List (Scrollable)
        self.scroll_frame = customtkinter.CTkScrollableFrame(self, label_text="Meine Charaktere")
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Form Frame (Add New)
        self.form_frame = customtkinter.CTkFrame(self)
        self.form_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self.create_form()
        self.load_characters()

    def create_form(self):
        # Input fields
        self.entry_name = customtkinter.CTkEntry(self.form_frame, placeholder_text="Name")
        self.entry_name.grid(row=0, column=0, padx=10, pady=10)

        self.entry_realm = customtkinter.CTkEntry(self.form_frame, placeholder_text="Realm")
        self.entry_realm.grid(row=0, column=1, padx=10, pady=10)

        self.entry_class = customtkinter.CTkEntry(self.form_frame, placeholder_text="Klasse")
        self.entry_class.grid(row=0, column=2, padx=10, pady=10)
        
        self.entry_race = customtkinter.CTkEntry(self.form_frame, placeholder_text="Volk")
        self.entry_race.grid(row=0, column=3, padx=10, pady=10)

        self.add_button = customtkinter.CTkButton(self.form_frame, text="Hinzufügen", command=self.add_character)
        self.add_button.grid(row=0, column=4, padx=10, pady=10)

    def load_characters(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        session = get_session(self.engine)
        characters = session.query(Character).all()
        session.close()

        for idx, char in enumerate(characters):
            self.create_character_row(idx, char)

    def create_character_row(self, idx, char):
        row_frame = customtkinter.CTkFrame(self.scroll_frame)
        row_frame.pack(fill="x", padx=5, pady=5)

        info_text = f"{char.name} ({char.race} {char.character_class}) - {char.realm} [{char.status}]"
        label = customtkinter.CTkLabel(row_frame, text=info_text, anchor="w")
        label.pack(side="left", padx=10)

        delete_btn = customtkinter.CTkButton(row_frame, text="Löschen", width=60, fg_color="red", hover_color="darkred",
                                             command=lambda c=char: self.delete_character(c.id))
        delete_btn.pack(side="right", padx=10, pady=5)

    def add_character(self):
        name = self.entry_name.get()
        realm = self.entry_realm.get()
        char_class = self.entry_class.get()
        race = self.entry_race.get()

        if not name or not realm:
            # Simplified error handling (terminal only as visual warning might be tricky without mainloop context yet)
            print("Error: Name and Realm are required.") 
            return

        session = get_session(self.engine)
        new_char = Character(name=name, realm=realm, character_class=char_class, race=race)
        session.add(new_char)
        session.commit()
        session.close()

        self.entry_name.delete(0, "end")
        self.entry_realm.delete(0, "end")
        self.entry_class.delete(0, "end")
        self.entry_race.delete(0, "end")
        
        self.load_characters()

    def delete_character(self, char_id):
        session = get_session(self.engine)
        char = session.query(Character).get(char_id)
        if char:
            session.delete(char)
            session.commit()
        session.close()
        self.load_characters()
