import asyncio
import json
from machine import Pin
import micropython
import network

# --- CONFIGURATION ---
# DO NOT EDIT BELOW. See README.md#configuration
### BEGIN GENERATED CONTENT
WIFI_SSID = ""
WIFI_PASS = ""
FIREBASE_HOSTNAME = ""
FIREBASE_SECRET = ""
DOOR_SENSOR_PIN = 14
RELAY_CONTROL_PIN = 99
DOOR_SENSOR_DEBOUNCE_MS = 50
### END GENERATED CONTENT
# --- END CONFIGURATION ---

# --- LED Control ---
#
# The Pico onboard LED will be used to indicate operating state
#
class Blink:
    # Define a bunch of LED blink patterns
    # First number is "on" time, second is "off" time (in seconds)
    BOOT = [.5, .5]
    WIFI_CONNECTING = [.1, .1]
    FIREBASE_IO = [1, 0]
    NORMAL = [.1, .4]
    DOOR_RELAY_CLOSED = [.02, .08]

    current = BOOT

    @staticmethod
    def set_blink(b):
        Blink.current = b

    @staticmethod
    async def activate():
        led = Pin("LED", Pin.OUT)

        while True:
            led.value(1)
            await asyncio.sleep(Blink.current[0])

            led.value(0)
            await asyncio.sleep(Blink.current[1])

# --- WIFI ---
async def connect_wifi():
    Blink.set_blink(Blink.WIFI_CONNECTING)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    print("Connecting to WiFi...")

    # Wait for connection with a timeout
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        await asyncio.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("Connected! IP:", wlan.ifconfig()[0])
        Blink.set_blink(Blink.NORMAL)
    else:
        print("WiFi failed. Retrying...")
        await asyncio.sleep(5)
        machine.reset()

# --- Door Sensor ---

# Allocate an emergency exception buffer for better debugging of errors within the ISR
micropython.alloc_emergency_exception_buf(100)

class DoorSensor:
    def __init__(self, pin_number, async_callback):
        """
        :param pin_number: which GPIO Pin to read from. Note: other side of switch should be wired to GND
        :param async_callback: an async callback called with a single string arg "OPEN" or "CLOSED"
        """
        self.pin_number = pin_number
        self.async_callback = async_callback

        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self.triggered = asyncio.ThreadSafeFlag()

    def _callback(self, ignored_pin):
        """
        ISR callback. We only signal to wake up the async handler using the flag 
        """
        self.triggered.set()

    async def activate(self):
        self.pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._callback)
        last_value = self.pin.value()
        while True:
            await self.triggered.wait()
            await asyncio.sleep_ms(DOOR_SENSOR_DEBOUNCE_MS)

            new_value = self.pin.value()
            if new_value == last_value:
                continue
            
            last_value = new_value
            state = "CLOSED" if new_value == 0 else "OPEN"

            print("door sensor signaled " + state)

            await self.async_callback(state)

# --- Firebase interactions ---

class Firebase:
    def __init__(self, db_hostname, db_secret):
        self.db_hostname = db_hostname
        self.db_secret = db_secret

    async def patch_data(self, path, data):
        """
        :param path: e.g. /garage
        :param data: a dict (not string) of data to set, e.g. {"status":"OPEN"}
        """
        json_body = json.dumps(data)
        content_length = len(json_body.encode('utf-8'))

        full_path = f"{path}.json?auth={self.db_secret}"

        request = (
            f"PATCH {full_path} HTTP/1.1\r\n"
            f"Host: {self.db_hostname}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {content_length}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{json_body}"
        )

        print("--- Patch Request: ---\n" + request)

        Blink.set_blink(Blink.FIREBASE_IO)

        reader, writer = await asyncio.open_connection(self.db_hostname, 443, ssl=True)

        try:
            writer.write(request.encode('utf-8'))
            await writer.drain()

            response = await reader.read(-1)
            print("--- Patch Response Received ---")
            print(response.decode('utf-8'))

        finally:
            writer.close()
            await writer.wait_closed()

        print("--- Patch done ---")

        Blink.set_blink(Blink.NORMAL)

#def trigger_relay():
#    """Simulates a physical button press."""
#    print("Action: Triggering Relay")
#    relay.value(1)
#    time.sleep(0.5)
#    relay.value(0)
#
#    # Wait for door to start moving, then update
#    time.sleep(2)
#    update_status()

#def listen_loop():
#    """Listens for 'OPEN' or 'CLOSE' commands."""
#    # We target the 'command' node specifically
#    url = f"{FIREBASE_URL}/command.json?auth={FIREBASE_SECRET}"
#
#    while True:
#        try:
#            # Short-poll listener for MicroPython stability
#            resp = urequests.get(url)
#            command = resp.json()
#            resp.close()
#
#            if command in ["OPEN", "CLOSE"]:
#                trigger_relay()
#                # Crucial: Reset command to IDLE so it doesn't trigger again
#                urequests.put(url, json="IDLE").close()
#
#            # Check sensor and sync status every 5 seconds regardless of commands
#            update_status()
#            time.sleep(5)
#
#        except Exception as e:
#            print("Loop Error:", e)
#            time.sleep(10)


async def main():
    t1 = Blink.activate()
    t2 = connect_wifi()

    firebase = Firebase(db_hostname=FIREBASE_HOSTNAME, db_secret=FIREBASE_SECRET)

    async def door_callback(state):
        await firebase.patch_data("/garage", {"status": state})

    door_sensor = DoorSensor(pin_number=DOOR_SENSOR_PIN, async_callback=door_callback)

    t3 = door_sensor.activate()

    # never expected to exit
    await asyncio.gather(t1, t2, t3)

# Run main() async
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Manual stop")
