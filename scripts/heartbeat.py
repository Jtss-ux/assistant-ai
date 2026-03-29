import httpx
import time
import os
import sys

# Get the Render URL from environment or use the one provided by user
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://assistant-ai-uqu4.onrender.com")
PING_ENDPOINT = f"{RENDER_URL.rstrip('/')}/ping"

def pulse():
    current_time = time.ctime()
    print(f"💓 [{current_time}] Sending heartbeat to {PING_ENDPOINT}...")
    headers = {"User-Agent": "AssistantHeartbeat/1.2 (Uptime Bot; Render Keep-Alive)"}
    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            response = client.get(PING_ENDPOINT)
            if response.status_code == 200 and response.text.strip('"') == "pong":
                print(f"✅ [{current_time}] Service is Awake!")
            else:
                print(f"⚠️ [{current_time}] Health check returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ [{current_time}] Heartbeat Failed: {e}")

if __name__ == "__main__":
    # If run manually, it does one pulse.
    # In a real daemon, you'd loop, but for GitHub Actions, one pulse is enough per run.
    pulse()
