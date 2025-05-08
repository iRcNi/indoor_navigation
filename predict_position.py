import subprocess
import re
import json
import math
import time
import cv2
import numpy as np

ESSID_FILTER = "KAU-INTERNET"
BSSID_LIST_FILE = "kau_bssids.txt"
DB_FILE = "wifi_fingerprint_data.json"
MAP_IMAGE = "CEIES_floorplan.jpg"
SCAN_INTERVAL = 5  # seconds

def get_iwlist_output(interface="wlp0s20f3"):
    result = subprocess.run(["sudo", "iwlist", interface, "scan"], capture_output=True, text=True)
    return result.stdout

def extract_rssi(iwlist_output, known_bssids):
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
    print(rssi_data)

    return rssi_data

def load_known_bssids():
    with open(BSSID_LIST_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def load_fingerprint_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def euclidean_distance(vec1, vec2, keys):
    return math.sqrt(sum((vec1.get(k, -100) - vec2.get(k, -100)) ** 2 for k in keys))

def predict_position(live_rssi, fingerprint_db, known_bssids):
    min_dist = float("inf")
    best_match = None

    for entry in fingerprint_db:
        db_rssi = entry["readings"]
        dist = euclidean_distance(live_rssi, db_rssi, known_bssids)
        if dist < min_dist:
            min_dist = dist
            best_match = entry["position"]

    return best_match

def draw_position(map_img, position):
    img = map_img.copy()
    grid_size = 26
    height, width, _ = img.shape
    px = int((position[0] - 1) / (grid_size - 1) * width)
    py = height - int((position[1] - 1) / (grid_size - 1) * height)
    print(position)

    cv2.circle(img, (px, py), 10, (0, 0, 255), -1)
    cv2.putText(img, f"({position[0]}, {position[1]})", (px + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return img

def main():
    map_img = cv2.imread(MAP_IMAGE)
    known_bssids = load_known_bssids()
    fingerprint_db = load_fingerprint_db()

    while True:
        iwlist_output = get_iwlist_output()
        live_rssi = extract_rssi(iwlist_output, known_bssids)
        position = predict_position(live_rssi, fingerprint_db, known_bssids)

        if position:
            img = draw_position(map_img, position)
            cv2.imshow("Live IPS", img)
        else:
            print("[-] Position not found.")
        
        if cv2.waitKey(1) == 27:  # ESC to exit
            break
        time.sleep(SCAN_INTERVAL)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()