# RealmGuardian

![Version](https://img.shields.io/badge/version-v.0.7.0-blue.svg)

RealmGuardian is a comprehensive web dashboard and background service designed to track your World of Warcraft economy. It integrates directly with the official Blizzard Battle.net API to fetch WoW Token prices, commodity market prices, and synchronized character wealth data across your entire account.

## Features (v.0.7.0)
- ✅ **New:** Automated Discord Weekly Reports (Wednesdays & Saturdays at 20:00).
- ✅ **New:** Windows Background Watchdog Daemon (auto-starts frontend/backend silently on PC boot).
- ✅ **New:** Modularized Backend Architecture (FastAPI with structured routing).
- ✅ **New:** GitHub Actions CI/CD Pipeline integration with `pytest`.
- ✅ Analytics Module for intelligent market scanning (Liquidity Score & Profitability).
- ✅ Interactive 14-day historical price graphs directly in the dashboard.
- ✅ Battle.net OAuth2 login flow is fully operational and correctly handles SSO redirects.
- ✅ Character Background Sync reliably imports character rosters, professions, item level, and gold sums.
- ✅ Live tracking for WoW Token prices with dynamic charting.
- ✅ Custom auction house commodity price history tracking.

## Project Structure
- `backend/routers/`: Contains all modular FastAPI routes (auth, dashboard, items, tasks, reports).
- `backend/scripts/`: Contains one-off migration and recovery scripts.
- `backend/background_tasks.py`: Houses the 30-minute sync loop and token refresh logic.
- `frontend/src/components/`: Contains all React UI widgets.
- `service/`: Windows background service installation scripts (`install_autostart_task.bat`, `start_services.bat`).

## Setup & Running
1. To run normally in dev mode: execute `run.bat` or `run_interactive.bat`.
2. To run as a background service:
   - Navigate to the `service` folder.
   - Run `install_autostart_task.bat` as Administrator.
   - Use `start_services.bat` and `stop_services.bat` to control the daemon.

---

> **Note for AI Agents & Developers:**
> The core login, OAuth, and Battle.net token synchronization loops are currently *robust and functioning correctly* as of `v.0.7.0`. Do not heavily modify the core `blizzard_api.py` authentication logic without extremely careful consideration.
