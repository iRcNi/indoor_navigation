import subprocess
import re
import os

ESSID_FILTER = "KAU-INTERNET"
LOG_FILE = "kau_bssids.txt"

def get_iwlist_output(interface="wlp4s0"):
    result = subprocess.run(["sudo", "iwlist", interface, "scan"], capture_output=True, text=True)
    return result.stdout

def extract_kau_bssids(iwlist_output):
    cells = iwlist_output.split("Cell ")
    bssids = []
    for cell in cells[1:]:
        essid_match = re.search(r'ESSID:"([^"]+)"', cell)
        if essid_match and essid_match.group(1) == ESSID_FILTER:
            bssid_match = re.search(r'Address: ([0-9A-Fa-f:]{17})', cell)
            if bssid_match:
                bssids.append(bssid_match.group(1))
    return bssids

def load_logged_bssids():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_new_bssids(new_bssids):
    with open(LOG_FILE, "a") as f:
        for bssid in new_bssids:
            f.write(bssid + "\n")
            print(f"[+] New BSSID added: {bssid}")

def main():
    iwlist_output = get_iwlist_output()
    current_bssids = extract_kau_bssids(iwlist_output)
    logged_bssids = load_logged_bssids()

    print(f"[=] Found {len(current_bssids)} BSSID(s) for ESSID '{ESSID_FILTER}'")

    new_bssids = [bssid for bssid in current_bssids if bssid not in logged_bssids]

    if new_bssids:
        save_new_bssids(new_bssids)
    else:
        print("[=] No new BSSIDs found.")

if __name__ == "__main__":
    main()
