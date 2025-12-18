import network
import urequests
import time
from machine import Pin

# --- CONFIGURATION ---
WIFI_SSID = "XXXX"
WIFI_PASS = "XXXX"
# Ensure the URL ends with /garage (matches your rules)
FIREBASE_URL = "https://XXXX-default-rtdb.firebaseio.com/garage"
FIREBASE_SECRET = "XXXX"

# --- PIN SETUP ---
relay = Pin("LED", Pin.OUT)
sensor = Pin(14, Pin.IN, Pin.PULL_UP)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("Connecting to WiFi...")
    
    # Wait for connection with a timeout
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        
    if wlan.isconnected():
        print("Connected! IP:", wlan.ifconfig()[0])
    else:
        print("WiFi failed. Retrying...")
        time.sleep(5)
        machine.reset()

def update_status():
    """Reads the magnetic sensor and pushes state to Firebase."""
    # sensor.value() == 0 means magnet is present (CLOSED)
    state = "CLOSED" if sensor.value() == 0 else "OPEN"
    url = f"{FIREBASE_URL}/status.json?auth={FIREBASE_SECRET}"
    try:
        # PUT overwrites the existing string
        resp = urequests.put(url, json=state)
        resp.close()
        print(f"Sync: Door is {state}")
    except Exception as e:
        print("Update Error:", e)

def trigger_relay():
    """Simulates a physical button press."""
    print("Action: Triggering Relay")
    relay.value(1)
    time.sleep(0.5) 
    relay.value(0)
    
    # Wait for door to start moving, then update
    time.sleep(2)
    update_status()

def listen_loop():
    """Listens for 'OPEN' or 'CLOSE' commands."""
    # We target the 'command' node specifically
    url = f"{FIREBASE_URL}/command.json?auth={FIREBASE_SECRET}"
    
    while True:
        try:
            # Short-poll listener for MicroPython stability
            resp = urequests.get(url)
            command = resp.json()
            resp.close()

            if command in ["OPEN", "CLOSE"]:
                trigger_relay()
                # Crucial: Reset command to IDLE so it doesn't trigger again
                urequests.put(url, json="IDLE").close()
            
            # Check sensor and sync status every 5 seconds regardless of commands
            update_status()
            time.sleep(5)

        except Exception as e:
            print("Loop Error:", e)
            time.sleep(10)

# --- EXECUTION ---
connect_wifi()
update_status()
listen_loop()
