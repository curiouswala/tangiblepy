import pluggy


hookimpl = pluggy.HookimplMarker('ampy2')

@hookimpl
def ampy2_firmware_download(config):
	config.pm.hook.device_firmware_download(config=config)


@hookimpl
def ampy2_firmware_install(config):
	config.pm.hook.device_firmware_install(config=config)


@hookimpl
def ampy2_connection_setup(config):
	config.pm.hook.device_connection_setup(config=config)
	

@hookimpl
def ampy2_verify_connection(config):
	config.pm.hook.device_verify_connection(config=config)



@hookimpl
def ampy2_remove_file(config, filename):
	config.pm.hook.device_remove_file(config=config,filename=filename)



@hookimpl
def ampy2_run_file(config, filename):
	config.pm.hook.device_run_file(config=config,filename=filename)

@hookimpl
def ampy2_files(config):
	config.pm.hook.device_files(config=config)

@hookimpl
def ampy2_shell(config):
	config.pm.hook.device_shell(config=config)

@hookimpl
def ampy2_copy(config, source, destination):
	config.pm.hook.device_copy(config=config, source=source, destination=destination)

@hookimpl
def ampy2_mkdir(config, dir_name):
	config.pm.hook.device_mkdir(config=config, dir_name=dir_name)

