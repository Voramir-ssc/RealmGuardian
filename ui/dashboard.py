import customtkinter
import threading
from modules.api_client import BlizzardAPIClient
from database import get_session
from models.price_data import Item, Price

class DashboardFrame(customtkinter.CTkFrame):
    def __init__(self, master, config, engine):
        super().__init__(master)
        self.config = config
        self.engine = engine
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1) # Alerts area expands

        # Header
        self.header = customtkinter.CTkLabel(self, text="Der Wächter - Dashboard", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.header.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")

        # Info Cards
        self.card_token = self.create_info_card(0, "WoW Token", "Lade...")
        self.card_realm = self.create_info_card(1, f"Realm: {self.config.get('realm_name', 'Unknown')}", "Lade...")

        # Alerts Section
        self.lbl_alerts = customtkinter.CTkLabel(self, text="Warnungen", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.lbl_alerts.grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        self.alerts_frame = customtkinter.CTkScrollableFrame(self)
        self.alerts_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")

        # Initial Load
        self.refresh_data()

    def create_info_card(self, col, title, initial_value):
        frame = customtkinter.CTkFrame(self)
        frame.grid(row=1, column=col, padx=20, pady=10, sticky="ew")
        
        lbl_title = customtkinter.CTkLabel(frame, text=title, font=customtkinter.CTkFont(size=12))
        lbl_title.pack(pady=(10, 0))
        
        lbl_value = customtkinter.CTkLabel(frame, text=initial_value, font=customtkinter.CTkFont(size=24, weight="bold"))
        lbl_value.pack(pady=(0, 10))
        
        return lbl_value

    def refresh_data(self):
        # Run API calls in background
        threading.Thread(target=self._fetch_live_data, daemon=True).start()
        self._check_alerts()

    def _fetch_live_data(self):
        if self.config.get('blizzard_client_id') == "YOUR_CLIENT_ID_HERE":
            self.card_token.configure(text="Konfiguration fehlt")
            self.card_realm.configure(text="Konfiguration fehlt")
            return

        client = BlizzardAPIClient(
            self.config['blizzard_client_id'], 
            self.config['blizzard_client_secret'],
            self.config.get('region', 'eu'), 
            self.config.get('locale', 'de_DE')
        )
        
        # Token
        try:
            price = client.get_wow_token_price()
            if price:
                self.card_token.configure(text=f"{int(price):,} Gold")
        except Exception as e:
            print(f"Dashboard Error (Token): {e}")

        # Realm
        try:
            # We need slug format (lowercase, dashes)
            realm_slug = self.config.get('realm_name', '').lower().replace(' ', '-')
            status = client.get_realm_status(realm_slug)
            self.card_realm.configure(text=status)
        except Exception as e:
            print(f"Dashboard Error (Realm): {e}")

    def _check_alerts(self):
        # Clear existing
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()

        session = get_session(self.engine)
        items = session.query(Item).filter(Item.min_price_threshold > 0).all()
        
        # We need the LATEST price for each item
        alerts_found = False
        
        for item in items:
            latest_price = session.query(Price).filter_by(item_id=item.id).order_by(Price.timestamp.desc()).first()
            
            if latest_price and latest_price.price < item.min_price_threshold:
                alerts_found = True
                self.create_alert_row(item, latest_price)

        session.close()
        
        if not alerts_found:
            lbl = customtkinter.CTkLabel(self.alerts_frame, text="Keine Warnungen.")
            lbl.pack(pady=10)

    def create_alert_row(self, item, price):
        frame = customtkinter.CTkFrame(self.alerts_frame, fg_color="darkred")
        frame.pack(fill="x", padx=5, pady=5)
        
        msg = f"ACHTUNG: {item.name} ist unter {item.min_price_threshold}g gefallen! Aktuell: {price.price:.2f}g"
        lbl = customtkinter.CTkLabel(frame, text=msg, text_color="white")
        lbl.pack(padx=10, pady=5)
