import subprocess
import re
import json
from datetime import datetime

target_ssids = ["Omar 4G", "Omar 4G_EXT", "Becon_1"]

def scan_wifi(interface="wlp4s0"):
    result = subprocess.run(
        ["sudo", "iwlist", interface, "scan"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = result.stdout

    rssi_data = {}
    blocks = output.split("Cell")
    for block in blocks:
        ssid_match = re.search(r'ESSID:"(.*?)"', block)
        rssi_match = re.search(r'Signal level=(-?\d+) dBm', block)
        if ssid_match and rssi_match:
            ssid = ssid_match.group(1)
            if ssid in target_ssids:
                rssi = int(rssi_match.group(1))
                rssi_data[ssid] = rssi

    return rssi_data

# === Scan and save ===
location = input("Enter (x,y) location: ")
scan_result = scan_wifi()

entry = {
    "location": location,
    "timestamp": datetime.now().isoformat(),
    "rssi": scan_result
}

# Append to file
with open("fingerprint_data.json", "a") as f:
    f.write(json.dumps(entry) + "\n")

print("Saved:", entry)
