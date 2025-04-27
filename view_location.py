import subprocess
import re
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.neighbors import KNeighborsRegressor

# === CONFIG ===
ap_list = ["Omar 4G", "Omar 4G_EXT", "Becon_1"]
interface = "wlan0"
scale = 100  # Pixels per meter (adjust to match your image)

# === Load your model (or paste model training here) ===
with open("fingerprint_data.json", "r") as f:
    X = []
    y = []
    for line in f:
        entry = json.loads(line)
        if(len(entry["location"].strip("()").split(",")) == 2):
            x, y_coord = map(float, entry["location"].strip("()").split(","))
            rssi_vector = []
            for ap in ap_list:
                rssi = entry["rssi"].get(ap, -100)
                rssi_vector.append(rssi)
            X.append(rssi_vector)
            y.append([x, y_coord])

model = KNeighborsRegressor(n_neighbors=3)
model.fit(X, y)

# === Live scan function ===
def live_scan(interface="wlp4s0"):
    subprocess.run(["sudo", "nmcli", "device", "wifi", "rescan"])
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
            if ssid in ap_list:
                rssi_data[ssid] = int(rssi_match.group(1))
    rssi_vector = [rssi_data.get(ap, -100) for ap in ap_list]
    return rssi_vector

# Load map and compute scaling
img = Image.open("image.png")
width, height = img.size
scale_x = width / 21
scale_y = height / 21

# Set up live plot
plt.ion()
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(img)
sc = ax.scatter([], [], c='red', s=100)

# Start live update
while True:
    try:
        rssi_vector = live_scan()
        x, y_ = model.predict([rssi_vector])[0]  # in meters

        # Convert to pixels
        px = x * scale_x
        py = height - (y_ * scale_y)  # Flip y

        sc.set_offsets([[px, py]])
        plt.pause(0.5)
        print(f"📍 X={x:.2f}m, Y={y_:.2f}m  ➜  px={px:.0f}, py={py:.0f}")

    except KeyboardInterrupt:
        print("Stopped.")
        break
