# AMPY-2

AMPY2 - Plugin based Python utility that replaces adafruit-ampy. It allows you to transfer and run your code on various IoT devices. This version supports WiFi as well as serial. This improves reliability and versatility.  The plugin-based architecture makes it modular and makes adding new features and support for various devices very simple.
	
It breaks backward compatibility since we are aiming to keep the commands Unix compatible. 
The plugin system is based on pluggy.

# Supported Devices
  * ESP32
### To be added
  * ESP8266
  * Pi Pico
  * Pi Zero W

# Installation
  * Download
  * pip install requirements.txt

# Usage
  * sudo python3 ampy2.py setup
  * sudo python3 ampy2.py ls 

# TODO
* PYPI launch
* Windows support
* Mac support
* GUI plugin
* EXE file
* Portable version
* Add example plugin 
* Add plugin tutorial
* Web UI plugin using flask


