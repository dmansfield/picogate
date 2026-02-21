# picogate

This folder contains an application to control garage doors using a Raspberry
Pico microcontroller, a Firebase realtime database, and a web app. In the
future an Android app will be supported as well.

The hardware has three main functions:
* Use a connected switch sensor to monitor a garage door to see if it's open
* Listen for a request (via Firebase) for a request to open the door
* Trigger the door to open using a relay

The code for the hardware is in the "hardware" folder. The Firebase 
setup is in the "cloud" folder. Each folder contains a README.md file with
more details.

*IMPORTANT* the Pico micropython script requires some secrets to be configured
in it. In order to prevent this from being pushed to the repository, a git
filter is used.

You'll need to configure your repository before using it by importing the
configuration file provided, .gitsharedconfig.

```
git config --local include.path ../.gitsharedconfig
```
