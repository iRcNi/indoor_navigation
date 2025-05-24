This project is a prototype of an indoor navigation program that uses RSSI data for the positioning and localization. By collecting enough data points, we implemented a KNN model that will take your current RSSI data and find the best match for it in that dataset and predicts the user position on the map.

brief description of the important files:

`CEIES_floorplan.jpg`
	A floor map of the targeted area for this project

`kau_bssid_logger.py` 
	Used for the data collection, where the user will enter it's current location (x,y on the image) and it will log the RSSI of the different BSSID (mac address) of the `kau_internt` network. This data will be used later for the model

`wifi_fingerprint_data.json`
	The collected data using the `kau_bssid_logger.py` file and it will be used for the model

`predict position.py`
  Is the main file for this project, it will read the current RSSI data of the user and find the best fit for it in the dataset using KNN and display a red dot on the map indicating the current position of the user
