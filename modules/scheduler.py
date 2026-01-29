import time
import threading
import schedule
from database import get_session
from models.price_data import Item, Price, TokenPrice
from modules.api_client import BlizzardAPIClient

class PriceScheduler:
    def __init__(self, config, engine):
        self.config = config
        self.engine = engine
        self.running = False
        self.thread = None
        self.api_client = None

    def start(self):
        if self.running:
            return
        
        # Initialize API Client only if config is valid (check existence of keys logic handled inside or here)
        if self.config.get('blizzard_client_id') == "YOUR_CLIENT_ID_HERE":
            print("Scheduler: API Credentials missing. Skipping.")
            return

        self.api_client = BlizzardAPIClient(
            self.config['blizzard_client_id'],
            self.config['blizzard_client_secret'],
            self.config.get('region', 'eu'),
            self.config.get('locale', 'de_DE')
        )

        self.running = True
        
        # Schedule the job (e.g., every 1 hour)
        # For testing, we might want it more frequent or triggerable manually.
        # Let's set it to every 60 minutes.
        schedule.every(60).minutes.do(self.update_prices)
        
        # Start thread
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("Scheduler started.")

    def _run_loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def update_prices(self):
        print("Scheduler: Updating prices...")
        try:
            session = get_session(self.engine)
            client = self.api_client

            # 1. Update Token Price
            try:
                token_price = client.get_wow_token_price()
                if token_price:
                    # Store in DB
                    new_token_price = TokenPrice(price=token_price)
                    session.add(new_token_price)
                    print(f"Stored Token Price: {token_price}g")
            except Exception as e:
                print(f"Error updating Token Price: {e}")

            # 2. Update Items
            items = session.query(Item).all()
            if not items:
                print("Scheduler: No items to track.")
                session.commit() # Save token price event if no items
                session.close()
                return

            # Fetch commodity auctions (Region-wide) for herbs
            # Note: This is an expensive call (large JSON), optimization might be needed
            # but for a desktop app local usage it's okay-ish.
            auctions = self.api_client.get_commodity_auctions()
            
            for item in items:
                price_gold = self.api_client.get_item_price(item.id, auctions)
                
                # Save to DB
                new_price = Price(item_id=item.id, price=price_gold)
                session.add(new_price)
                
            session.commit()
            session.close()
            print("Scheduler: Prices updated.")
        except Exception as e:
            print(f"Scheduler Error: {e}")
