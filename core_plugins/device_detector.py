import pluggy
import esptool
from loguru import logger
import time 
import serial
import os
import subprocess as sp





hookimpl = pluggy.HookimplMarker('ampy2')






@hookimpl
def detector_plugin(config):
	device_list = ['esp32']
	import serial.tools.list_ports

	port_list = serial.tools.list_ports.comports()

	print("Device Types:")

	for count, device in enumerate(device_list):
		print(f"{count+1}: {device}")


	device_name = input(">> Select Device Type (1): ").strip()




	print("Serial_Ports:")
	for count, port in enumerate(port_list):
		print(f'{count+1}: {port.device}')


	serial_port = input(">> Serial Port (1): ").strip()


	if device_name == '':
		device_name = device_list[0]
	else:
		device_name = device_list[int(device_name)-1]

	if serial_port == '':
		serial_port = port_list[0].device
	else:
		serial_port = port_list[int(serial_port)-1]

	config.store['device'] = device_name
	config.store['serial_port'] = serial_port



	


@hookimpl
def detect_micropython(config):
	config.store['mpy_installed'] = False

