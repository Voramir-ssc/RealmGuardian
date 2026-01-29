import customtkinter
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from database import get_session
from models.price_data import Item, Price

class TreasuryFrame(customtkinter.CTkFrame):
    def __init__(self, master, engine):
        super().__init__(master)
        self.engine = engine
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2) # Chart area larger
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = customtkinter.CTkLabel(self, text="Schatzamt - Preisüberwachung", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.header.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")

        # Left Side: Item List & Management
        self.left_frame = customtkinter.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=1)

        self.lbl_items = customtkinter.CTkLabel(self.left_frame, text="Beobachtete Items", font=customtkinter.CTkFont(weight="bold"))
        self.lbl_items.grid(row=0, column=0, padx=10, pady=10)

        self.item_list_frame = customtkinter.CTkScrollableFrame(self.left_frame)
        self.item_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add Item Form
        self.add_frame = customtkinter.CTkFrame(self.left_frame)
        self.add_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.entry_search = customtkinter.CTkEntry(self.add_frame, placeholder_text="Item Name suchen...")
        self.entry_search.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.add_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_search = customtkinter.CTkButton(self.add_frame, text="🔍", width=30, command=self.search_item_api)
        self.btn_search.grid(row=0, column=1, padx=5, pady=5)

        # Search Results (Popup or list below?)
        # For simplicity, let's add a listbox/scrollframe for results below the search bar
        self.search_results_frame = customtkinter.CTkScrollableFrame(self.left_frame, height=100)
        self.search_results_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        
    def search_item_api(self):
        query = self.entry_search.get()
        if not query or len(query) < 2:
            return
            
        # Get Client from App config
        # We need to access the app's config. Currently passed to App, but TreasuryFrame has only engine.
        # Let's fix this constructor in app.py or pass config here.
        # Assuming we update App to pass config or we get it via master.
        
        # HACK: Retrieve config from master (App)
        config = self.master.config
        from modules.api_client import BlizzardAPIClient
        
        if config.get('blizzard_client_id') == "YOUR_CLIENT_ID_HERE":
             messagebox.showerror("Fehler", "API nicht konfiguriert!")
             return

        try:
            client = BlizzardAPIClient(config['blizzard_client_id'], config['blizzard_client_secret'], config.get('region'), config.get('locale'))
            results = client.search_item(query)
            
            # Clear previous results
            for w in self.search_results_frame.winfo_children():
                w.destroy()
                
            if not results:
                customtkinter.CTkLabel(self.search_results_frame, text="Keine Treffer").pack()
                return

            for item in results:
                btn = customtkinter.CTkButton(self.search_results_frame, text=f"{item['name']} ({item['id']})", 
                                              anchor="w", fg_color="transparent", border_width=1,
                                              command=lambda i=item: self.add_item_from_search(i))
                btn.pack(fill="x", padx=2, pady=2)
                
        except Exception as e:
            print(f"Search Error: {e}")

    def add_item_from_search(self, item_data):
        session = get_session(self.engine)
        # Check if exists
        existing = session.query(Item).get(item_data['id'])
        if existing:
             messagebox.showinfo("Info", "Item bereits in der Liste.")
             session.close()
             return

        new_item = Item(id=item_data['id'], name=item_data['name'], expansion="Unknown")
        session.add(new_item)
        session.commit()
        session.close()
        
        # Clear search
        self.entry_search.delete(0, "end")
        for w in self.search_results_frame.winfo_children():
            w.destroy()
            
        # Refresh List
        self.load_items()

    def load_items(self):
        # Clear existing buttons
        for widget in self.item_list_frame.winfo_children():
            widget.destroy()

        session = get_session(self.engine)
        items = session.query(Item).all()
        session.close()

        for item in items:
            btn = customtkinter.CTkButton(self.item_list_frame, text=item.name, 
                                          command=lambda i=item.id: self.show_chart(i),
                                          fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
            btn.pack(fill="x", padx=5, pady=2)
            
        print(f"Loaded {len(items)} items into list.") # Debug
        self.current_item_id = item_id
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        session = get_session(self.engine)
        item = session.query(Item).get(item_id)
        prices = session.query(Price).filter_by(item_id=item_id).order_by(Price.timestamp).all()
        session.close()

        if not prices:
            lbl = customtkinter.CTkLabel(self.chart_frame, text="Keine Daten verfügbar")
            lbl.pack(expand=True)
            return

        dates = [p.timestamp for p in prices]
        values = [p.price for p in prices]

        # Matplotlib Figure
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(dates, values, marker='o')
        ax.set_title(f"Preisverlauf: {item.name}")
        ax.set_xlabel("Zeit")
        ax.set_ylabel("Gold")
        ax.grid(True)
        
        # Dark mode adjustment for matplotlib
        fig.patch.set_facecolor('#2b2b2b') # approximate dark gray
        ax.set_facecolor('#2b2b2b')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white') 
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
