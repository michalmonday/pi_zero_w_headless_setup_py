
It's a script that automates the process of editing files to enable SSH, set WIFI and SSH credentials.

This way, the process of getting pi zero W ready from scratch is:
* flash SD card using Rufus and 32-bit R-Pi OS Bullseye (legacy)  
* run `pi_zero_w_headless_setup.py`  
* ssh into the board (`ssh pi@raspberrypi.local`), (user=pi, password=raspberry),   

It was tested using the following image file:  
`2024-10-22-raspios-bullseye-armhf-lite.img`

# Pre-requisites
Before running the script, the following environment variables must be set:
* WIFI_SSID   
* WIFI_PASSWORD  

Alternatively, you can edit the script and hardcode the values (search for "WIFI_SSID" and "WIFI_PASSWORD" in the script).

# What it does
* creates an empty file called "ssh"  
* appends `dtoverlay=dwc2` to the end of the "config.txt" file  
* inserts `modules-load=dwc2,g_ether` after `rootwait` in the "cmdline.txt" file  
* creates "userconf.txt" file with the following content (corresponding to username=pi, password=raspberry):  
```
pi:$6$/4.VdYgDm7RJ0qM1$FwXCeQgDKkqrOU3RIRuDSKpauAbBvP11msq9X58c8Que2l1Dwq3vdJMgiZlQSbEXGaY5esVHGBNbCxKLVNqZW1
```
* creates a file called "wpa_supplicant.conf" file with the following content:  
```
country=gb
update_config=1
ctrl_interface=/var/run/wpa_supplicant

network={
    scan_ssid=1
    ssid=WIFI_SSID (environment variable)
    psk=WIFI_PASSWORD (environment variable)
}
```

