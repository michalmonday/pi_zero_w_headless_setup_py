
It's a script that automates the process of editing files to enable SSH, set WIFI and SSH credentials.

The process of getting pi zero W ready from scratch is:
* flash SD card using Rufus and 32-bit R-Pi OS Bullseye (legacy)
* run `pi_zero_w_headless_setup.py`
* ssh into the board (`ssh pi@raspberrypi.local`), (user=pi, password=raspberry), 
