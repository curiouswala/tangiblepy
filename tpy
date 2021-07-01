#!/usr/bin/env python3
import pluggy
from core_plugins import core, device_detector
from core_plugins.configure import Config
import sys
from plugins import esp32_plugin, pico_plugin, esp8266_plugin, db_storage
import os
import time
from loguru import logger
PLUGINS_LIST = [core, device_detector, esp32_plugin, pico_plugin, esp8266_plugin, db_storage]
# PLUGINS_SPEC = [core_spec,device_detector_spec,esp32_plugin_spec, pico_plugin_spec, esp8266_plugin_spec]

SETTINGS = {'download_path':'downloads',
			'db_filename':'db.json'}

def device_setup(config):
	config.pm.hook.detector_plugin(config=config)    #core_plugins/device_detector.py
	config.pm.hook.detect_micropython(config=config) #core_plugins/device_detector.py	
	
	config.pm.hook.ampy2_firmware_download(config=config)
	config.pm.hook.ampy2_firmware_install(config=config)

	config.pm.hook.ampy2_connection_setup(config=config)
	config.pm.hook.device_verify_connection(config=config)



def main():
	pm = pluggy.PluginManager('ampy2')
	for plugin in PLUGINS_LIST:
		pm.register(plugin)
	# pm.check_pending()

	config = Config(pm)
	for setting_key,setting_value in SETTINGS.items():
		config.store[setting_key]=setting_value

	config.pm.hook.get_db_store(config=config,datatype='wifi')
	wifi_dic = config.store.get('wifi')
	logger.debug(wifi_dic)
	if wifi_dic:
		config.store['device'] = wifi_dic['device_name']


	

	if sys.argv[1] == 'setup':
		device_setup(config)


	elif sys.argv[1] == 'rm':
		file_or_folder_name = sys.argv[2]
		config.pm.hook.device_remove_file(config=config, filename=file_or_folder_name)


	elif sys.argv[1] == 'run':
		filename = sys.argv[2]
		pre,ext = os.path.splitext(filename)
		config.pm.hook.device_run_file(config=config, filename=pre)

	elif sys.argv[1] == 'ls':
		config.pm.hook.device_files(config=config)

	elif sys.argv[1] == 'shell':
		config.pm.hook.device_shell(config=config)

	elif sys.argv[1] == 'cp':
		source = sys.argv[2]
		destination = sys.argv[3]
		config.pm.hook.device_copy(config=config,source=source, destination=destination)

	elif sys.argv[1] == 'mkdir':
		dir_name = sys.argv[2]
		config.pm.hook.device_mkdir(config=config,dir_name=dir_name)



	elif sys.argv[1] == 'connect':
		'''
		ampy2.py connect device_name device_pin ssid password ip

		'''
		config.store['wifi']['device_name'] = sys.argv[2]
		config.store['wifi']['device_pin'] = sys.argv[3]
		config.store['wifi']['SSID'] = sys.argv[4]
		config.store['wifi']['password'] = sys.argv[5]
		config.store['wifi']['ip_address'] = sys.argv[6]
		config.store['mpy_installed'] = True
		config.store['device'] = config.store['wifi']['device_name']
		config.pm.hook.device_verify_connection(config=config)


	elif sys.argv[1] == 'putdir':
		source = os.path.join('projects',sys.argv[2])
		dest = sys.argv[3]
		config.pm.hook.device_send_file(config=config, source=source, dest=dest, project=True)






		
		






	
if __name__ == '__main__':
	main()