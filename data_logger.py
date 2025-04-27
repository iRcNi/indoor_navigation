import subprocess
import re
import os
import json
import sys

ESSID_FILTER = "KAU-INTERNET"
BSSID_LIST_FILE = "kau_bssids.txt"
OUTPUT_FILE = "wifi_fingerprint_data.json"

def get_iwlist_output(interface="wlp4s0"):
    result = subprocess.run(["sudo", "iwlist", interface, "scan"], capture_output=True, text=True)
    return result.stdout

def extract_rssi_per_bssid(iwlist_output, known_bssids):
    cells = iwlist_output.split("Cell ")
    rssi_data = {}

    for cell in cells[1:]:
        bssid_match = re.search(r'Address: ([0-9A-Fa-f:]{17})', cell)
        essid_match = re.search(r'ESSID:"([^"]+)"', cell)
        rssi_match = re.search(r'Signal level=(-\d+) dBm', cell)

        if bssid_match and essid_match and essid_match.group(1) == ESSID_FILTER:
            bssid = bssid_match.group(1)
            if bssid in known_bssids and rssi_match:
                rssi = int(rssi_match.group(1))
                rssi_data[bssid] = rssi

    return rssi_data

def load_known_bssids():
    if not os.path.exists(BSSID_LIST_FILE):
        return set()
    with open(BSSID_LIST_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_reading(position, rssi_data):
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            all_data = json.load(f)
    else:
        all_data = []

    entry = {
        "position": position,
        "readings": rssi_data
    }
    all_data.append(entry)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
    print(f"[+] Recorded data at position {position}")

def main():
    if len(sys.argv) != 3:
        print("Usage: sudo python3 data_logger.py <x> <y>")
        sys.exit(1)

    try:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
        if not (1 <= x <= 26 and 1 <= y <= 26):
            raise ValueError
    except ValueError:
        print("Error: x and y must be integers between 1 and 26.")
        sys.exit(1)

    position = [x, y]
    known_bssids = load_known_bssids()
    iwlist_output = get_iwlist_output()
    rssi_data = extract_rssi_per_bssid(iwlist_output, known_bssids)

    print(f"[=] Found {len(rssi_data)} BSSIDs with signal at position {position}")

    if not rssi_data:
        print("[-] No known BSSID RSSI values found at this location.")
    else:
        save_reading(position, rssi_data)

if __name__ == "__main__":
    main()
