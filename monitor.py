# monitor.py
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

def check_health():
    try:
        response = requests.get("https://kenyavault.co.ke", timeout=10)
        if response.status_code == 200:
            logging.info("✅ App is healthy")
            return True
        else:
            logging.error(f"❌ App returned status: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    while True:
        check_health()
        time.sleep(60)  # Check every minute
