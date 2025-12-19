# Hardware

## IMPORTANT
Read the parent README.md

## Parts List

| Component       | Part/Model  |
| --------------- | ----------- |
| Microcontroller | Raspberry Pi Pico WH - Pico Wireless with Headers Soldered (ID:5544)
| Relay Module    | Adafruit Power Relay FeatherWing (ID:3191)
| Magnetic Switch | Magnetic contact switch (door sensor) (ID:375)
| Enclosure       | Small Plastic Project Enclosure - Weatherproof with Clear Top (ID:903)


## Wiring

| Device | Connection A | Connection B |
| ------ | ------------ | ------------ |
|Relay Power|Relay 3V → Pico 3V3|Relay GND → Pico GND
Relay Signal|Relay Signal → Pico GP15|—
Door Sensor|Sensor Wire 1 → Pico GP14|Sensor Wire 2 → Pico GND
Opener Motor|Relay COM → Motor Button Terminal|Relay NO → Motor Button Terminal

## Pico Software

### Micropython Firmware Installation

Visit [raspberrypi.com](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html). Follow instructions...

Basically:
 1. Download the right firmware file for your device (Pico W probably)
 2. Press and hold the small BOOTSEL button while connecting the device to your laptop.
 3. Release the BOOTSEL button, the device will appear as a USB drive.
 4. Copy (drag/drop) the downloaded firmware file - device will reboot.

### Confirming It Works

Download and install Thonny (python IDE), run it.

Select the "micropython" runtime via menu in bottom-right. Note: you *may* have to update OS permissions in Linux to grant access, e.g. 
```
sudo usermod -a -G dialout $USER
```

In the REPL (bottom window) you should see "Micropython "...

In the REPL, type 
```
print("hello picogate")
``` 
and you should see it printed back. Congrats!

### System Installation

The actual software for the device is `main.py`. 

There are some variables in the script you'll need to edit. To get the database secret, you need to go set up all the cloud stuff first see [../cloud/README.md](../cloud/README.md). Then go to the Firebase Console, click the "gear" next to your project. In project settings, go to Service Account and unmask the Database Secret.

To install the garage opener code on the Pico:

 1. Connect your Pico W to your computer.
 2. Update your WiFi, Firebase URL, and Secret etc. in the file.
 3. Copy/paste the script into Thonny (I couldn't get Thonny to open a file... wat?)
 4. Click File > Save As and select Raspberry Pi Pico. Name the file main.py. (Naming it main.py tells the Pico to run this automatically every time it gets power).

You can immediately run it by clicking the green triangle, or you can power cycle the thing by entering:
```
import machine
machine.reset()
```
in the REPL.

## Configuration
In order to prevent sensitive data from being committed to the `main.py` file,
a git filter is used (`../scripts/config_swap_filter.sh`).

This filter must be manually added to your git config (see parent README.md).

The filter swaps in two different versions of the configuration into the body
of the `main.py` file, between the sentinel lines:

```
### BEGIN GENERATED CONTENT
[ content in here is replaced ]
### END GENERATED CONTENT
```

Two different versions of this content must exist, one of which you'll need
to create and won't get checked in:
 * `configuration.py.clean` is checked in and maintained by repo owners
 * `configuration.py.sensitive` should be a copy maintained by you

Note: you may need to manually add new keys if they're added during future
development. Feel free to improve the config management and send a pull req.
