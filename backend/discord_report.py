"""
discord_report.py
Generates and sends the weekly RealmGuardian report to Discord.
"""
import requests
from datetime import datetime, timedelta
import json
from config import config
import models
from database import SessionLocal

def format_gold(copper):
    if not copper: return "0g"
    return f"{int(copper / 10000):,.0f}g"

def send_weekly_report():
    if not config.discord_webhook_url:
        print("No Discord Webhook URL configured.")
        return

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # 1. Fetch Current Status
        latest_token = db.query(models.WowTokenHistory).order_by(models.WowTokenHistory.last_updated_timestamp.desc()).first()
        current_token_price = latest_token.price if latest_token else 0
        
        all_chars = db.query(models.Character).all()
        current_total_gold = sum(c.gold for c in all_chars)
        
        richest_char = max(all_chars, key=lambda c: c.gold) if all_chars else None
        
        # 2. Fetch Last Snapshot for Delta
        last_snapshot = db.query(models.WeeklyReportSnapshot).order_by(models.WeeklyReportSnapshot.timestamp.desc()).first()
        
        delta_gold = current_total_gold - last_snapshot.total_gold if last_snapshot else 0
        delta_token = current_token_price - last_snapshot.wow_token_price if last_snapshot else 0
        
        # 3. Markt Tops & Flops
        top_winner = None
        top_loser = None
        winner_diff = 0
        loser_diff = 0
        
        tracked_items = db.query(models.TrackedItem).all()
        target_time = last_snapshot.timestamp if last_snapshot else (now - timedelta(days=7))
        
        for item in tracked_items:
            current_price_record = db.query(models.ItemPriceHistory).filter(models.ItemPriceHistory.item_id == item.id).order_by(models.ItemPriceHistory.timestamp.desc()).first()
            if not current_price_record: continue
            current_price = current_price_record.buyout
            
            old_price_record = db.query(models.ItemPriceHistory)\
                .filter(models.ItemPriceHistory.item_id == item.id)\
                .filter(models.ItemPriceHistory.timestamp <= target_time)\
                .order_by(models.ItemPriceHistory.timestamp.desc()).first()
                
            if old_price_record:
                diff = current_price - old_price_record.buyout
                if diff > winner_diff:
                    winner_diff = diff
                    top_winner = f"{item.name} (+{format_gold(diff)})"
                elif diff < loser_diff:
                    loser_diff = diff
                    top_loser = f"{item.name} ({format_gold(diff)})"

        if not top_winner: top_winner = "Keine Daten"
        if not top_loser: top_loser = "Keine Daten"

        # 4. Main Character Data
        main_name = config.main_character.get("name", "Lenmera")
        main_realm = config.main_character.get("realm", "Die Aldor")
        main_char = db.query(models.Character).filter_by(name=main_name, realm=main_realm).order_by(models.Character.level.desc()).first()
        
        ilvl_delta_str = ""
        professions_delta_str = ""
        current_professions = main_char.professions if main_char else None

        if main_char and last_snapshot:
            # iLvl
            ilvl_diff = main_char.item_level - (last_snapshot.main_char_ilvl or 0)
            if ilvl_diff > 0:
                ilvl_delta_str = f" (+{ilvl_diff})"
            elif ilvl_diff < 0:
                ilvl_delta_str = f" ({ilvl_diff})"
            else:
                ilvl_delta_str = " (unverändert)"
                
            # Professions
            if last_snapshot.main_char_professions and current_professions:
                try:
                    old_profs = json.loads(last_snapshot.main_char_professions)
                    new_profs = json.loads(current_professions)
                    
                    old_map = {}
                    for p in old_profs:
                        for t in p.get("tiers", []):
                            old_map[f"{p['name']} - {t['name']}"] = t["skill_points"]
                            
                    new_map = {}
                    for p in new_profs:
                        for t in p.get("tiers", []):
                            new_map[f"{p['name']} - {t['name']}"] = t["skill_points"]
                            
                    deltas = []
                    for k, new_val in new_map.items():
                        old_val = old_map.get(k, 0)
                        if new_val > old_val:
                            deltas.append(f"{k}: +{new_val - old_val} (jetzt {new_val})")
                            
                    if deltas:
                        professions_delta_str = "\n".join(deltas)
                    else:
                        professions_delta_str = "Keine Skillpunkt-Veränderung."
                except Exception as e:
                    professions_delta_str = "Fehler beim Parsen der Berufe."
                    print(f"Profession JSON Error: {e}")
            else:
                professions_delta_str = "Neu erfasst."

        # 5. Build Embed
        embed = {
            "title": "📜 RealmGuardian Wochenbericht",
            "color": 16766720, # Gold Color
            "footer": {"text": f"Generiert am {now.strftime('%d.%m.%Y %H:%M')}"},
            "fields": []
        }
        
        # Wirtschaft
        gold_emoji = "📈" if delta_gold >= 0 else "📉"
        token_emoji = "📈" if delta_token >= 0 else "📉"
        
        delta_gold_str = f"+{format_gold(delta_gold)}" if delta_gold >= 0 else f"{format_gold(delta_gold)}"
        delta_token_str = f"+{format_gold(delta_token)}" if delta_token >= 0 else f"{format_gold(delta_token)}"
        
        embed["fields"].append({
            "name": "💰 Finanz-Bilanz",
            "value": f"**Account-Gold:** {format_gold(current_total_gold)}\n**Veränderung:** {delta_gold_str} {gold_emoji}\n**Reichster Charakter:** {richest_char.name if richest_char else 'N/A'} ({format_gold(richest_char.gold if richest_char else 0)})",
            "inline": False
        })
        
        embed["fields"].append({
            "name": "⚖️ Markt-Tops & Flops",
            "value": f"**🚀 Top-Gewinner:** {top_winner}\n**📉 Top-Verlierer:** {top_loser}",
            "inline": False
        })
        
        embed["fields"].append({
            "name": "🪙 WoW-Token",
            "value": f"**Aktueller Preis:** {format_gold(current_token_price)}\n**Veränderung:** {delta_token_str} {token_emoji}",
            "inline": False
        })
        
        # Main Character
        if main_char:
            main_val = f"**Item Level:** {main_char.item_level}{ilvl_delta_str}\n"
            main_val += f"**Delves abgeschlossen:** {main_char.delves_completed}\n"
            main_val += f"**Höchstes Delve-Tier:** {main_char.delves_max_tier}\n"
            
            if professions_delta_str:
                main_val += f"\n**⚒️ Berufe-Fortschritt:**\n{professions_delta_str}"
                
            if len(main_val) <= 1024:
                embed["fields"].append({
                    "name": f"⭐ Hauptcharakter: {main_char.name}",
                    "value": main_val,
                    "inline": False
                })
            else:
                chunks = [main_val[i:i+1024] for i in range(0, len(main_val), 1024)]
                embed["fields"].append({
                    "name": f"⭐ Hauptcharakter: {main_char.name}",
                    "value": chunks[0],
                    "inline": False
                })
                for chunk in chunks[1:]:
                    embed["fields"].append({
                        "name": "⭐ (Fortsetzung)",
                        "value": chunk,
                        "inline": False
                    })
        else:
            embed["fields"].append({
                "name": "⭐ Hauptcharakter",
                "value": f"Charakter '{main_name}' auf '{main_realm}' nicht in der Datenbank gefunden.",
                "inline": False
            })
            
        payload = {
            "username": "RealmGuardian",
            "avatar_url": "https://wow.zamimg.com/images/wow/icons/large/inv_misc_coin_01.jpg",
            "embeds": [embed]
        }
        
        # 6. Send to Discord
        headers = {"Content-Type": "application/json"}
        response = requests.post(config.discord_webhook_url, data=json.dumps(payload), headers=headers)
        
        if response.status_code in [200, 204]:
            print("Weekly report sent to Discord successfully.")
            # 7. Save new snapshot
            new_snap = models.WeeklyReportSnapshot(
                total_gold=current_total_gold,
                wow_token_price=current_token_price,
                timestamp=now,
                main_char_ilvl=main_char.item_level if main_char else 0,
                main_char_professions=current_professions
            )
            db.add(new_snap)
            db.commit()
        else:
            print(f"Failed to send to Discord: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error generating Discord report: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Test execution
    send_weekly_report()
