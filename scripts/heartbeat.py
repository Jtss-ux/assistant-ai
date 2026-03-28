import httpx
import time
import os
import sys

# Get the Render URL from environment or use the one provided by user
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://assistant-ai-uqu4.onrender.com")
PING_ENDPOINT = f"{RENDER_URL.rstrip('/')}/ping"

def pulse():
    print(f"💓 Sending heartbeat to {PING_ENDPOINT}...")
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(PING_ENDPOINT)
            if response.status_code == 200 and response.text.strip('"') == "pong":
                print("✅ Service is Awake!")
            else:
                print(f"⚠️ Health check returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Heartbeat Failed: {e}")

if __name__ == "__main__":
    # If run manually, it does one pulse.
    # In a real daemon, you'd loop, but for GitHub Actions, one pulse is enough per run.
    pulse()
