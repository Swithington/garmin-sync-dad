"""
Debug script — checks what activities Garmin returns for a specific date range.
Run this in GitHub Actions to see exactly what the API is returning.
"""

import os
import json
import pickle
from datetime import date, timedelta
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

GARMIN_EMAIL    = os.environ["GARMIN_EMAIL"]
GARMIN_PASSWORD = os.environ["GARMIN_PASSWORD"]
TOKEN_DIR       = os.path.expanduser("~/.garminconnect")

def get_client():
    token_file  = os.path.join(TOKEN_DIR, "oauth2_token.json")
    pickle_file = os.path.join(TOKEN_DIR, "session.pkl")
    client = Garmin(email=GARMIN_EMAIL, password=GARMIN_PASSWORD)
    if os.path.exists(token_file):
        try:
            client.login(token_file)
            return client
        except Exception:
            pass
    if os.path.exists(pickle_file):
        try:
            with open(pickle_file, "rb") as f:
                client = pickle.load(f)
            return client
        except Exception:
            pass
    client.login()
    return client

client = get_client()
print("Connected to Garmin\n")

# Check a window around the gap — last known run to 3 months after
check_dates = [
    "2026-02-01", "2026-02-02", "2026-02-03", "2026-02-04",
    "2026-02-05", "2026-02-06", "2026-02-07", "2026-02-08",
    "2026-02-09", "2026-02-10", "2026-02-15", "2026-02-20",
    "2026-02-28", "2026-03-01", "2026-03-15", "2026-04-01",
    "2026-04-15", "2026-05-01", "2026-05-15", "2026-06-01",
    "2026-06-15", "2026-07-01", "2026-07-15",
]

print(f"{'Date':<14} {'Activities found':<20} {'Types'}")
print("-" * 60)

for date_str in check_dates:
    try:
        raw = client.get_activities_by_date(date_str, date_str)
        if raw:
            types = [a.get("activityType", {}).get("typeKey", "unknown") for a in raw]
            print(f"{date_str:<14} {len(raw):<20} {', '.join(types)}")
        else:
            print(f"{date_str:<14} 0")
    except Exception as e:
        print(f"{date_str:<14} ERROR: {e}")

# Also try a broad search for recent activities
print("\n--- Broad search: last 50 activities ---")
try:
    recent = client.get_activities(0, 50)
    for a in recent[:10]:
        print(f"  {a.get('startTimeLocal', '')[:10]}  {a.get('activityType', {}).get('typeKey', '')}  {a.get('activityName', '')}")
    if len(recent) > 10:
        print(f"  ... and {len(recent) - 10} more")
except Exception as e:
    print(f"  ERROR: {e}")
