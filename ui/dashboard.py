import customtkinter
import threading
from modules.api_client import BlizzardAPIClient
from database import get_session
from models.price_data import Item, Price, TokenPrice
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from tkinter import filedialog, messagebox
from import_characters import import_characters

class DashboardFrame(customtkinter.CTkFrame):
    def __init__(self, master, config, engine):
        super().__init__(master)
        self.config = config
        self.engine = engine
        
        # --- Main Grid Configuration ---
        # Use a single column for the main container or 2 equal columns?
        # Let's stick to 2 equal columns for the cards, but the main frame should catch resizing.
        self.grid_columnconfigure(0, weight=1, uniform="group1")
        self.grid_columnconfigure(1, weight=1, uniform="group1")
        self.grid_rowconfigure(2, weight=1) # Charts area expands

        # --- Header (Row 0) ---
        self.header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        
        self.header_label = customtkinter.CTkLabel(
            self.header_frame, 
            text="Realm Guardian", 
            font=customtkinter.CTkFont(family="Roboto", size=24, weight="bold")
        )
        self.header_label.pack(side="left", anchor="w")
        
        # Import Button (Right side of header)
        self.btn_import = customtkinter.CTkButton(
            self.header_frame,
            text="Charaktere Importieren",
            command=self.import_characters_dialog,
            width=140,
            height=30
        )
        self.btn_import.pack(side="right", anchor="e")

        # --- Info Cards (Row 1) ---
        # Container is not strictly necessary if we grid cards directly, 
        # but helpful for spacing. Let's grid directly to avoid inner-frame complexity.
        
        self.card_token = self.create_infocard_frame(self, 0, "WoW Marke", "Lade...", "💰")
        self.card_realm = self.create_infocard_frame(self, 1, f"Realm: {self.config.get('realm_name', 'Unk')}", "Check...", "🌍")



        # --- Chart Section ---
        self.chart_frame = customtkinter.CTkFrame(self, fg_color=("gray95", "gray17"), corner_radius=10)
        self.chart_frame.grid(row=2, column=0, columnspan=2, padx=30, pady=20, sticky="nsew")

        # --- Alerts Section ---
        self.lbl_alerts = customtkinter.CTkLabel(
            self, 
            text="Markt Warnungen", 
            font=customtkinter.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        self.lbl_alerts.grid(row=3, column=0, columnspan=2, padx=30, pady=(10, 5), sticky="w")

        self.alerts_frame = customtkinter.CTkScrollableFrame(self, height=150, fg_color="transparent")
        self.alerts_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 30), sticky="nsew")

        # Initial Load
        self.refresh_data()



    def refresh_data(self):
        # Run API calls in background
        threading.Thread(target=self._fetch_live_data_background, daemon=True).start()
        self._check_alerts()
        self._draw_token_chart()

    def create_infocard_frame(self, parent, col, title, initial_value, icon):
        frame = customtkinter.CTkFrame(parent, corner_radius=10)
        frame.grid(row=1, column=col, padx=20, pady=10, sticky="ew")
        
        lbl_title = customtkinter.CTkLabel(frame, text=title, font=customtkinter.CTkFont(size=12, weight="bold"), text_color="gray70")
        lbl_title.pack(padx=15, pady=(15, 5), anchor="w")
        
        lbl_value = customtkinter.CTkLabel(frame, text=initial_value, font=customtkinter.CTkFont(size=24, weight="bold"))
        lbl_value.pack(padx=15, pady=(0, 15), anchor="w")
        
        # Store icon/title if needed later, but we mainly need to update value
        return lbl_value

    def _fetch_live_data_background(self):
        """Fetch data in thread, then schedule UI update on main thread."""
        data = {"token": None, "realm": None, "error_token": False}
        
        try:
            # 1. DB Fallback
            try:
                session = get_session(self.engine)
                latest = session.query(TokenPrice).order_by(TokenPrice.timestamp.desc()).first()
                session.close()
                if latest:
                    data["token"] = latest.price
            except Exception:
                pass

            # 2. API
            if self.config.get('blizzard_client_id') and self.config.get('blizzard_client_id') != "YOUR_CLIENT_ID_HERE":
                try:
                    client = BlizzardAPIClient(
                        self.config['blizzard_client_id'], 
                        self.config['blizzard_client_secret'],
                        self.config.get('region', 'eu'), 
                        self.config.get('locale', 'de_DE')
                    )
                    price = client.get_wow_token_price()
                    if price:
                        data["token"] = price
                    
                    realm_slug = self.config.get('realm_name', '').lower().replace(' ', '-')
                    data["realm"] = client.get_realm_status(realm_slug)
                except Exception as e:
                    print(f"API Error: {e}")
                    if data["token"] is None:
                        data["error_token"] = True

        except Exception as e:
            print(f"Background Fetch Error: {e}")
        
        # Schedule UI update on main thread
        self.after(0, lambda: self._update_ui_with_data(data))

    def _update_ui_with_data(self, data):
        """Update UI elements. Must run on main thread."""
        # Token
        if data["token"]:
            self.card_token.configure(text=f"{int(data['token']):,} G")
        elif data["error_token"]:
            self.card_token.configure(text="Fehler")
        else:
            self.card_token.configure(text="N/A")

        # Realm
        if data["realm"]:
            self.card_realm.configure(text=data["realm"])
        else:
            # Keep default or show sim status if strictly offline
            pass


    def import_characters_dialog(self):
        filename = filedialog.askopenfilename(
            title="Charakter-Datei auswählen",
            filetypes=[("Excel oder CSV", "*.xlsx *.csv")]
        )
        
        if filename:
            try:
                # Run the import logic
                # We could capture stdout here or modify import_characters to return status
                # For now, just running it.
                import_characters(filename)
                messagebox.showinfo("Import", "Import abgeschlossen! Bitte App neu starten um Daten zu sehen.")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def _draw_token_chart(self):
        # Clear previous
        for widget in self.chart_frame.winfo_children():
             widget.destroy()

        session = get_session(self.engine)
        prices = session.query(TokenPrice).order_by(TokenPrice.timestamp).all()
        session.close()

        if not prices:
             msg = customtkinter.CTkLabel(self.chart_frame, text="Keine Daten für Diagramm verfügbar.")
             msg.pack(expand=True)
             return

        dates = [p.timestamp for p in prices]
        values = [p.price for p in prices]

        # Figure
        fig = Figure(figsize=(8, 3.5), dpi=100) # Increased Size
        ax = fig.add_subplot(111)
        
        # Plot
        ax.plot(dates, values, color='#FFC107', linewidth=2, linestyle='-', marker='o', markersize=4) # Added marker
        ax.fill_between(dates, values, alpha=0.1, color='#FFC107')
        
        # Axes Styling
        ax.set_title("WoW Token Preisverlauf (letzte 365 Tage)", color="gray", pad=20, loc='left', fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.4, color="gray")
        
        # Style
        # Match roughly with Dark theme
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#555555')
        ax.tick_params(axis='x', colors='#888888', labelsize=8)
        ax.tick_params(axis='y', colors='#888888', labelsize=8)
        
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=45) # Rotate labels
        
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _check_alerts(self):
        # Clear existing
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()

        session = get_session(self.engine)
        items = session.query(Item).filter(Item.min_price_threshold > 0).all()
        
        alerts_found = False
        
        for item in items:
            latest_price = session.query(Price).filter_by(item_id=item.id).order_by(Price.timestamp.desc()).first()
            
            if latest_price and latest_price.price < item.min_price_threshold:
                alerts_found = True
                self.create_alert_row(item, latest_price)

        session.close()
        
        if not alerts_found:
            lbl = customtkinter.CTkLabel(self.alerts_frame, text="Keine aktuellen Warnungen.", text_color="gray50")
            lbl.pack(pady=20)

    def create_alert_row(self, item, price):
        # Modern Alert Row
        frame = customtkinter.CTkFrame(self.alerts_frame, fg_color=("gray90", "gray25"), corner_radius=6)
        frame.pack(fill="x", padx=10, pady=5)
        
        # Highlighting strip
        strip = customtkinter.CTkFrame(frame, width=5, fg_color="#E74C3C", corner_radius=0)
        strip.pack(side="left", fill="y")
        
        content = customtkinter.CTkFrame(frame, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        # Top line: Item Name
        lbl_name = customtkinter.CTkLabel(content, text=item.name, font=customtkinter.CTkFont(size=14, weight="bold"))
        lbl_name.pack(anchor="w")
        
        # Bottom line: Details
        diff = item.min_price_threshold - price.price
        details = f"Aktuell: {price.price:.0f}g  |  Unter Limit ( {item.min_price_threshold}g ) um {diff:.0f}g"
        lbl_details = customtkinter.CTkLabel(content, text=details, font=customtkinter.CTkFont(size=12), text_color="#E74C3C")
        lbl_details.pack(anchor="w")
