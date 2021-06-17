from tkinter import *
from tkinter import StringVar
from functools import partial
from tkinter import messagebox


import pluggy
from loguru import logger
import requests
import os
import time
import serial
import webrepl
import json

import watchdog.events 
import watchdog.observers 

# logger.remove()
# logger.add(sys.stderr, level='INFO')


hookimpl = pluggy.HookimplMarker('ampy2')

DEVICE = 'esp32'



@hookimpl
def device_firmware_download(config):
	if config.store['device'] == DEVICE:
		url = 'https://micropython.org/resources/firmware/esp32-idf3-20200902-v1.13.bin'
		firmware_path = os.path.join(config.store['download_path'], url.split("/")[-1])

		if config.store['device'] == DEVICE:
			logger.debug('Downloading firmware for esp32')
			if os.path.isfile(firmware_path):
				logger.debug('file exist')
			else:
				logger.debug('File downloading...')
				r = requests.get(url)
				with open(firmware_path,'wb') as f:
					f.write(r.content)

		config.store['firmware_path'] = firmware_path
		logger.debug(f'Firmware at {firmware_path}')


@hookimpl
def device_firmware_install(config):
	if config.store['device'] == DEVICE:
		logger.debug(config.store)
		if config.store['mpy_installed'] == False and config.store['device'] == DEVICE:
			answer = input('>> Install Firmware y/n (y): ')

			if answer == 'yes' or answer == 'y' or answer == '':
				print("Cleaning Device in Process...")
				os.system(f"esptool.py --port {config.store['serial_port']} --baud 115200 erase_flash")
				logger.debug('esp32_firmware_installing calling...')
				os.system(f"esptool.py --port {config.store['serial_port']} --baud 115200 write_flash -z 0x1000 {config.store['firmware_path']}")
				time.sleep(1)
				config.pm.hook.detect_micropython(config=config)
				config.store['mpy_installed'] = True
			else:
				config.store['mpy_installed'] = True


@hookimpl
def device_connection_setup(config):
	if config.store['device'] == DEVICE:

		logger.debug('esp32_connection_setup calling...')
		logger.debug(config.store)


		if config.store['mpy_installed'] == True and config.store['device'] == DEVICE:
			config.pm.hook.get_db_store(config=config,datatype='wifi')
			logger.debug(len(config.store['wifi']))

			
			if config.store['wifi']:
				print(config.store['wifi'])
				answer = input(">> Use Above WiFi Settings  y/n (y):  ")
				if answer=='y' or answer=='Y' or answer=='':
					logger.debug('Using old wifi configration.')
				else:
					ssid = input("WiFi SSID: ")
					password = input("WiFi Password: ")
					device_pin = input("Device Pin (4 digit): ")
					config.store['wifi']['SSID'] = ssid
					config.store['wifi']['password'] = password
					config.store['wifi']['device_pin']=device_pin
					config.store['wifi']['device_name']= config.store['device']
			else:
				ssid = input("WiFi SSID: ")
				password = input("WiFi Password: ")
				device_pin = input("Device Pin (4 digit): ")
				config.store['wifi']['SSID'] = ssid
				config.store['wifi']['password'] = password
				config.store['wifi']['device_pin']=device_pin
				config.store['wifi']['device_name']= config.store['device']

				

			print('Setting up WiFi...')
			logger.debug(config.store)



			path = os.getcwd()

			espfiles_path = os.path.join(path,'espfiles') 
			logger.debug(espfiles_path)

			port = config.store['serial_port']
			ssid = config.store['wifi']['SSID']
			password = config.store['wifi']['password']
			device_pin = config.store['wifi']['device_pin']

			with open(espfiles_path+'/replconf.py','w') as f:
				f.write(f"ssid='{ssid}'\npassword='{password}'\n")


			with open(espfiles_path+'/webrepl_cfg.py','w') as f:
				f.write(f"PASS='{device_pin}'\n")


			ser = serial.Serial()
			ser.baudrate = 115200
			ser.port = port
			ser.close()
			time.sleep(1)
			ser.open()

			logger.debug('Starting files puting in a device.')
			# files_list = ['boot.py','replconf.py','webrepl_cfg.py','blink.py','utils.py','tree.py']
			files_list = os.listdir('espfiles/')
			for file in files_list:
				os.system(f"ampy -p {port} -b 115200 put espfiles/{file}")
				logger.debug(file)


			ser.write(b'import machine\n\rmachine.reset()\n\r')
			while True:
				line = ser.readline()
				clean_line = line.decode('utf8')
				text = 'WebREPL daemon started on ws'
				if text in clean_line:
					ip_address = clean_line.split('//')[-1].split(':')[0]
					config.store['wifi']['ip_address']= ip_address
					if ip_address:
						break

			logger.debug(ip_address)
			


def make_webrepl(config):
	if config.store['device'] == DEVICE:
		config.pm.hook.get_db_store(config=config,datatype='wifi')
		repl=webrepl.Webrepl(**{'host':config.store['wifi']['ip_address'],'port':8266,'password':config.store['wifi']['device_pin']})
		config.store['repl'] = repl
		logger.debug("repl setup")

@hookimpl
def device_verify_connection(config):
	if config.store['device'] == DEVICE:
		logger.debug('Testing Device Connection...')
		if config.store.get('repl') == None:
			make_webrepl(config)
		config.store['repl'].sendcmd(f"import utils,blink;utils.reload(blink)")
		ip_address = config.store['wifi']['ip_address']
		print(f"Device Connected Successfully @ {ip_address}")


@hookimpl
def device_remove_file(config,filename):
	if config.store['device'] == DEVICE:
		if config.store.get('repl') == None:
			make_webrepl(config)
		config.store['repl'].sendcmd(f"from utils import rm; rm('{filename}')")


@hookimpl
def device_run_file(config,filename):
	if config.store['device'] == DEVICE:
		if config.store.get('repl') == None:
			make_webrepl(config)
		result = config.store['repl'].sendcmd(f"import utils,{filename};utils.reload({filename})")
		cleaned_output = "\n".join(result.decode().strip().split("\n")[1:])
		print(cleaned_output)

@hookimpl
def device_files(config):
	logger.debug(config.store)
	if config.store['device'] == DEVICE:
		if config.store.get('repl') == None:
			make_webrepl(config)
		if len(sys.argv) > 2:
			folder_name = sys.argv[2]
			resp=config.store['repl'].sendcmd(f"import os; os.listdir('{folder_name}')")
		else:
			resp=config.store['repl'].sendcmd("import os; os.listdir()")
		logger.debug(resp)
		cleaned_output = "\n".join(resp.decode().strip().split("\n")[1:])
		cleaned_output = cleaned_output.replace("'",'"')
		file_list = json.loads(cleaned_output)
		cleaned_output = "\t".join(file_list)
		print(cleaned_output)

@hookimpl
def device_shell(config):
	if config.store['device'] == DEVICE:
		if config.store.get('repl') == None:
			make_webrepl(config)
		print(f'MicroPython Shell - {DEVICE}')
		print(f'Type <exist> to close the shell')
		while True:
			user_input = input(">>> ")
			if user_input == 'exit':
				break
			resp=config.store['repl'].sendcmd(user_input)
			cleaned_output = "\n".join(resp.decode().strip().split("\n")[1:])
			print(cleaned_output)


@hookimpl
def device_copy(config, source, destination):
	if config.store['device'] == DEVICE:

		if config.store.get('repl') == None:
			make_webrepl(config)

		#Destination is PC
		
		if source.startswith('device:'):
			source = source.replace('device:','')
			if destination.endswith('/'):
				destination = os.path.join(destination, os.path.basename(source))
			config.store['repl'].get_file(source, destination)


		#Destination is Device

		elif destination.startswith('device:'):
			destination = destination.replace('device:','')
			if destination.endswith('/'):
				destination = os.path.join(destination, os.path.basename(source))
				logger.debug(destination)


			if os.path.isfile(source):
				print("isfile_source: ",source)
				print("isfile_destination: ",destination)
				config.store['repl'].put_file(source, destination)

			elif os.path.isdir(source):
				main_folder = source
				for root, dirs, files in os.walk(source):
					print(root)
					# config.pm.hook.device_mkdir(config=config, dir_name=root)

					for dir in dirs:
						# dir_name = os.path.join(root,file)
						print(dir)
						print('dir:',os.path.join(root,dir))
						config.pm.hook.device_mkdir(config=config, dir_name=dir)

					for file in files:
						source = os.path.join(root,file)
						print('file:',file)
						print("Source: ",source)
						print("Walk_folder: ",destination)

						config.pm.hook.device_copy(config=config, source=source, destination="device:"+source.replace(main_folder,''))
						# config.store['repl'].put_file(source, destination)

				



@hookimpl
def device_mkdir(config, dir_name):
	if config.store['device'] == DEVICE:
		if config.store.get('repl') == None:
			make_webrepl(config)
		resp=config.store['repl'].sendcmd(f"import os; os.mkdir('{dir_name}')")



		



