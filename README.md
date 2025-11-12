# Battletech-tageting-computer
A simple hand held to hit calculator for the BattleTech minitures board game. 
![IMG_20251112_135142710_HDR](https://github.com/user-attachments/assets/3a924765-9aa7-4111-96a3-27899de5fdcc)

Define the mechs you are playing with in `mechs.json`. The weapons lists are already in this code will allow the device to calculate the to hit from the range etc. You adjust which mech your on and the various stats with the encoders and it automatically updates.

It was all hand soldered, so no pcb or circuit diagrams currently. If there is any intrest ping me and I will draw some up. 

This is running on [CircuitPython](https://circuitpython.org/). So the entry point into the code is `code.py`. 

This runs on a [Raspberry pi Pico](https://www.adafruit.com/product/4864), with a [2.7" Sharp Memory display](https://www.adafruit.com/product/4694) and 6 rotatry encoders. Power is provided by 2 AAA batteries, which can directly drive everything. Don't forget a backflow diode for the batteries. As if you plug in the usb micro at the same time as the batteries are on you will cook them.
