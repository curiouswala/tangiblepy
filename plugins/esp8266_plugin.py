import pluggy


hookimpl = pluggy.HookimplMarker('ampy2')

@hookimpl
def device_firmware_Download(config):
	if config.store['device'] == "esp8266":
		print('Downloading firmware for esp8266')
		config.store['firmware_path'] = 'path'


@hookimpl
def device_firmware_installing(config):
	print('ampy2_firmware_installing calling...')


@hookimpl
def device_connection_setup(config):
	print('ampy2_connection_setup calling...')

@hookimpl
def device_verify_connection(config):
	print('ampy2_verify_connection calling...')