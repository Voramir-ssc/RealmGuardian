import customtkinter
from database import init_db
from modules.scheduler import PriceScheduler
from ui.dashboard import DashboardFrame
from ui.barracks import BarracksFrame
from ui.treasury import TreasuryFrame
class App(customtkinter.CTk):
    def __init__(self, config):
        super().__init__()

        self.config = config
        self.title("Realm Wächter")
        self.geometry("1100x580")

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create Navigation Frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Realm Wächter",
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Navigation Buttons
        self.btn_dashboard = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Dashboard",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, sticky="ew")

        self.btn_barracks = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Kaserne",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.show_barracks)
        self.btn_barracks.grid(row=2, column=0, sticky="ew")

        self.btn_treasury = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Schatzamt",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.show_treasury)
        self.btn_treasury.grid(row=3, column=0, sticky="ew")

# Main Content Frames
        # Ensure DB is ready
        self.engine = init_db() 
        
        # Start Scheduler
        self.scheduler = PriceScheduler(self.config, self.engine)
        self.scheduler.start()
        
        self.dashboard_frame = DashboardFrame(self, self.config, self.engine)
        self.dashboard_frame.grid(row=0, column=1, sticky="nsew")

        self.barracks_frame = BarracksFrame(self, self.engine)

        self.treasury_frame = TreasuryFrame(self, self.engine)

        # Select default
        self.select_frame_by_name("dashboard")

    def show_dashboard(self):
        self.select_frame_by_name("dashboard")

    def show_barracks(self):
        self.select_frame_by_name("barracks")

    def show_treasury(self):
        self.select_frame_by_name("treasury")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.btn_dashboard.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.btn_barracks.configure(fg_color=("gray75", "gray25") if name == "barracks" else "transparent")
        self.btn_treasury.configure(fg_color=("gray75", "gray25") if name == "treasury" else "transparent")

        # show selected frame
        if name == "dashboard":
            self.barracks_frame.grid_forget()
            self.treasury_frame.grid_forget()
            self.dashboard_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "barracks":
            self.dashboard_frame.grid_forget()
            self.treasury_frame.grid_forget()
            self.barracks_frame.grid(row=0, column=1, sticky="nsew")
            # Auto-refresh when showing the tab
            self.barracks_frame.load_characters()
        elif name == "treasury":
            self.dashboard_frame.grid_forget()
            self.barracks_frame.grid_forget()
            self.treasury_frame.grid(row=0, column=1, sticky="nsew")


