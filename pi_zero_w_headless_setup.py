
import pathlib
import os
import sys
import string
import ctypes
from ctypes import wintypes
import argparse

parser = argparse.ArgumentParser(description="Setup a Raspberry Pi Zero W for headless operation")
parser.add_argument("--override-file-check", action="store_true", help="Override the check for existing files on the drive")
args = parser.parse_args()

PI_ZERO_DEVICE_NAME = "bootfs"

# this will allow to get info about drives to only shortlist those that include "bootfs" in the label
# to minimize risk of accidentally selecting the wrong drive
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

def get_drive_label(drive):
    volume_name_buffer = ctypes.create_unicode_buffer(261)
    file_system_name_buffer = ctypes.create_unicode_buffer(261)
    serial_number = wintypes.DWORD()
    max_component_length = wintypes.DWORD()
    file_system_flags = wintypes.DWORD()

    result = kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive),
        volume_name_buffer,
        ctypes.sizeof(volume_name_buffer),
        ctypes.byref(serial_number),
        ctypes.byref(max_component_length),
        ctypes.byref(file_system_flags),
        file_system_name_buffer,
        ctypes.sizeof(file_system_name_buffer),
    )
    
    if result:
        return volume_name_buffer.value
    return "No Label"

def list_drives_with_names():
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            label = get_drive_label(drive)
            drives.append((drive, label))
    return drives

def select_drive_with_name():
    drives = list_drives_with_names()
    if not drives:
        print("No drives found.")
        return None
    filtered_drives = [drive for drive in drives if PI_ZERO_DEVICE_NAME in drive[1]]
    print("Available drives:")
    for i, (drive, label) in enumerate(filtered_drives, 1):
        print(f"{i}. {drive} - {label}")
    print()
    while True:
        try:
            choice = int(input(f"Select a drive\n> "))
            if 1 <= choice <= len(filtered_drives):
                return filtered_drives[choice - 1][0]  # Return only the drive letter
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def verify_drive_by_content(drive_letter):
    files_that_should_exist = ["cmdline.txt", "config.txt", "kernel.img", "start.elf"]
    for file in files_that_should_exist:
        file_path = os.path.join(drive_letter, file)
        if not os.path.exists(file_path):
            print(f"File {file} not found in the selected drive.")
            return False
    return True

# Example usage
selected_drive = select_drive_with_name()
if not selected_drive:
    print("No drive selected. Exiting")
    sys.exit(1)

if args.override_file_check:
    print("Skipping file check")
else:
    if not verify_drive_by_content(selected_drive):
        print("Selected drive does not contain the necessary files (use --override-file-check option to ignore this). Exiting")
        sys.exit(1)

# create empty ssh file in the bootfs directory
ssh_file_path = os.path.join(selected_drive, "ssh")
is_ssh_file_present = os.path.exists(ssh_file_path)
if not is_ssh_file_present:
    print("Creating empty ssh file")
    with open(ssh_file_path, "w") as f:
        pass
else:
    print("ssh file already present")

# append the following line to the config.txt file if it is not already at the end of the file
# dtoverlay=dwc2
config_file_path = os.path.join(selected_drive, "config.txt")
append_line = False
with open(config_file_path, "r") as f:
    lines = f.readlines()
    if not lines[-1].strip() == "dtoverlay=dwc2":
        append_line = True
if append_line:
    print("Adding dtoverlay=dwc2 to config.txt")
    lines.append("\ndtoverlay=dwc2\n")
    with open(config_file_path, "w") as f:
        f.writelines(lines)
else:
    print("dtoverlay=dwc2 already present in config.txt")

# open config.txt and insert the following between "rootwait" and "quiet" but only if it is not already present
# modules-load=dwc2,g_ether
cmd_file_path = os.path.join(selected_drive, "cmdline.txt")
with open(cmd_file_path, "r") as f:
    data = f.read()
    if "modules-load=dwc2,g_ether" not in data:
        print("Adding modules-load=dwc2,g_ether to cmdline.txt")
        data = data.replace("rootwait", "rootwait modules-load=dwc2,g_ether")
    else:
        print("modules-load=dwc2,g_ether already present in cmdline.txt")
    with open(cmd_file_path, "w") as f:
        f.writelines(data)

# create a file named wpa_supplicant.conf 
wpa_supplicant_file_path = os.path.join(selected_drive, "wpa_supplicant.conf")
is_wpa_supplicant_file_present = os.path.exists(wpa_supplicant_file_path)
if not is_wpa_supplicant_file_present:
    print("Creating wpa_supplicant.conf file with wifi credentials")
    wpa_supplicant_content = f"""country=gb
    update_config=1
    ctrl_interface=/var/run/wpa_supplicant

    network={{
        scan_ssid=1
        ssid="{os.environ['WIFI_SSID']}"
        psk="{os.environ['WIFI_PASSWORD']}"
        }}"""
    with open(wpa_supplicant_file_path, "w") as f:
        f.write(wpa_supplicant_content)
else:
    print("wpa_supplicant.conf file already present")

userconfig_file_path = os.path.join(selected_drive, "userconf.txt")
is_userconfig_file_present = os.path.exists(userconfig_file_path)
if not is_userconfig_file_present:
    print("Creating userconf.txt file with hash of ssh password (username:pi password:raspberry)")
    with open(userconfig_file_path, "w") as f:
        # the long hash is the hash of the password "raspberry"
        # as described in the comment by André Kuhlmann at this StackOverflow question: 
        # https://stackoverflow.com/questions/71804429/raspberry-pi-ssh-access-denied
        f.write(f"pi:$6$/4.VdYgDm7RJ0qM1$FwXCeQgDKkqrOU3RIRuDSKpauAbBvP11msq9X58c8Que2l1Dwq3vdJMgiZlQSbEXGaY5esVHGBNbCxKLVNqZW1")
else:
    print("userconfig.txt file already present")

print("Setup complete.")
        





