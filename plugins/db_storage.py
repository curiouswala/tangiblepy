import pluggy
from loguru import logger
from TinnyStore import PermanentStore

hookimpl = pluggy.HookimplMarker('ampy2')

@hookimpl
def get_db_store(config, datatype):
	db_filename = config.store['db_filename']
	db_store = PermanentStore(db_filename=db_filename,datatype=datatype)
	config.store[datatype] = db_store