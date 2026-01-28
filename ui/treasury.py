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
        
        self.entry_id = customtkinter.CTkEntry(self.add_frame, placeholder_text="ID")
        self.entry_id.grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = customtkinter.CTkEntry(self.add_frame, placeholder_text="Name")
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)
        self.btn_add = customtkinter.CTkButton(self.add_frame, text="+", width=30, command=self.add_item)
        self.btn_add.grid(row=0, column=2, padx=5, pady=5)

        # Right Side: Chart
        self.right_frame = customtkinter.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.chart_frame = customtkinter.CTkFrame(self.right_frame, fg_color="transparent")
        self.chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.load_items()
        self.current_item_id = None

    def load_items(self):
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
            
    def add_item(self):
        try:
            item_id = int(self.entry_id.get())
            name = self.entry_name.get()
        except ValueError:
            return

        if not name:
            return

        session = get_session(self.engine)
        new_item = Item(id=item_id, name=name, expansion="Unknown")
        session.add(new_item)
        session.commit()
        session.close()
        
        self.entry_id.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.load_items()

    def show_chart(self, item_id):
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
