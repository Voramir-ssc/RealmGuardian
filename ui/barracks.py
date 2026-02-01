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
        # Card style frame
        row_frame = customtkinter.CTkFrame(
            self.scroll_frame, 
            fg_color=("white", "gray25") if idx % 2 == 0 else ("gray95", "gray20"),
            corner_radius=6
        )
        row_frame.pack(fill="x", padx=10, pady=5)

        # Status Indicator (Color Strip)
        status_color = "#2ECC71" if char.status == "Aktiv" else "#95A5A6"
        status_strip = customtkinter.CTkFrame(row_frame, width=5, fg_color=status_color)
        status_strip.pack(side="left", fill="y", padx=(0, 10))

        # Main Info (Name & Race/Class)
        info_frame = customtkinter.CTkFrame(row_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=5)
        
        lbl_name = customtkinter.CTkLabel(info_frame, text=char.name, font=customtkinter.CTkFont(size=14, weight="bold"))
        lbl_name.pack(anchor="w")
        
        lbl_details = customtkinter.CTkLabel(
            info_frame, 
            text=f"{char.race} {char.character_class} - {char.realm}", 
            font=customtkinter.CTkFont(size=12),
            text_color="gray60"
        )
        lbl_details.pack(anchor="w")

        # Professions (Right side)
        prof_text = f"{char.profession_1 or '-'} / {char.profession_2 or '-'}"
        lbl_prof = customtkinter.CTkLabel(row_frame, text=prof_text, font=customtkinter.CTkFont(size=12), text_color="gray70")
        lbl_prof.pack(side="right", padx=20)

        # Delete Button
        delete_btn = customtkinter.CTkButton(
            row_frame, 
            text="✕", 
            width=30, 
            height=30,
            fg_color="transparent", 
            text_color=("red", "#E74C3C"),
            hover_color=("gray90", "gray30"),
            command=lambda c=char: self.delete_character(c.id)
        )
        delete_btn.pack(side="right", padx=5)

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
