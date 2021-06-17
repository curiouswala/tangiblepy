# AMPY-2 ALPHA

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
* setup device - sudo python3 ampy2.py setup
* remove file/folder - ampy2.py rm <file_name> or <folder_name>
* run - ampy2.py run <file_name>
* ls - ampy2.py ls or ls <folder_name>
* shell - ampy2.py shell
* cp - ampy2.py cp source device:destination (put files)
* cp - ampy2.py cp device:source destination (get files)
* mkdir - ampy2.py mkdir <folder_name>
* connect - ampy2.py connect device_name device_pin ssid password ip 

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
* Add support for live-coding
* Add support for rustpad.io 
* Device Auto-Discovery
* Support arrow keys in the shell

# Made by
* [Hasan](https://curiouswala.com/)
* [Gaurav](https://gauravn.com/)


