import pluggy
from loguru import logger

hookimpl = pluggy.HookimplMarker('ampy2')

@hookimpl
def device_firmware_Download(config):
	if config.store['device'] == "pico":
		logger.debug('Downloading firmware for pico')
		config.store['firmware_path'] = 'path'


@hookimpl
def device_firmware_installing(config):
	logger.debug('ampy2_firmware_installing calling...')


@hookimpl
def device_connection_setup(config):
	logger.debug('ampy2_connection_setup calling...')

@hookimpl
def device_verify_connection(config):
	logger.debug('ampy2_verify_connection calling...')