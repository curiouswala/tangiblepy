import pluggy

hookspec = pluggy.HookspecMarker('ampy2')

@hookspec
def core_spec(config: dict):
	"""
	Basic plugin spec

	Takes one arguments: config

	arguments type: dict
	"""