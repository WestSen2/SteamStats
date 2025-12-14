
# SteamStats
Simple testing of SteamAPI, produces steam profiles stats of inputed Steam ID

## Requirements
- Python 3.11+ (any 3.x release that Streamlit supports)
- `pip` package manager

## Setup
1. Clone the repository if you haven't already:
   ```bash
   git clone https://github.com/WestSen2/SteamStats.git
   cd SteamStats
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\\Scripts\\activate  # Windows PowerShell
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   If a `requirements.txt` file is not present yet, install the key dependencies manually:
   ```bash
   pip install streamlit pandas requests prettytable
   ```

## Running the Dashboard
1. With the virtual environment activated, run:
   ```bash
   ```
2. A browser window or tab will open automatically. Enter a Steam ID (the default is `STEAM_ID` defined in `SteamStat.py`) and click **Fetch stats**.

## What You Get
- Player summary, status, visibility, and profile metadata.
- Owned games table with total/average hours and last-played details per platform.
- Friends table with online/offline breakdown and raw API payload expanders for deep inspection.
