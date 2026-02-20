# RealmGuardian

![Version](https://img.shields.io/badge/version-v.0.4.2-blue.svg)

RealmGuardian is a comprehensive web dashboard and background service designed to track your World of Warcraft economy. It integrates directly with the official Blizzard Battle.net API to fetch WoW Token prices, commodity market prices, and synchronized character wealth data across your entire account.

## Current Working Status (v.0.4.2)
- ✅ Battle.net OAuth2 login flow is fully operational and correctly handles SSO redirects.
- ✅ Character Background Sync reliably imports character rosters and gold sums (filters unavailable/ghost characters).
- ✅ Live tracking for WoW Token prices.
- ✅ Custom auction house commodity price history tracking.
- ❌ Account Playtime has been permanently removed as it is no longer provided by the public Blizzard Web API.

## Backlog / Planned Features
- [ ] **Historische Gold-Charts:** Tägliche Snapshots des Account-übergreifenden Goldes mit visueller Darstellung.
- [ ] **Item Level (iLvl) & Ausrüstung:** Detaillierte Ansicht der angelegten Ausrüstung und Item-Level pro Charakter.
- [ ] **Berufe:** Übersicht der Berufe und Skill-Level der Charaktere.

---

> **Note for AI Agents & Developers:**
> The core login, OAuth, and Battle.net token synchronization loops are currently *robust and functioning correctly* as of `v.0.4.2`. Do not heavily modify the core `blizzard_api.py` authentication logic or the recursive callback loops in `main.py` without extremely careful consideration.
