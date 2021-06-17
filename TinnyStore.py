from tinydb import TinyDB, Query

class PermanentStore(dict):
    def __init__(self,*arg,**kw):
        super(PermanentStore, self).__init__(*arg, **kw)
        self.db = self._database_init(kw['db_filename'])
        self.datatype = kw['datatype'] 
        self.data = Query()
        self._datatype_init()
        
    def _datatype_init(self):
        returndata = self.db.search(self.data.type == self.datatype)
        if len(returndata)==0:
            self.db.insert({'type': self.datatype})

    def _database_init(self, db_filename):
        db = TinyDB(db_filename)
        return db

    def clear_db(self):
        self.db.truncate()


    def __getitem__(self, key):
        # value = super().__getitem__(key)
        wifidict = self.db.search(self.data.type == self.datatype)[0]
        return wifidict.get(key)

        return_str = f'{type(value)} : {value}'
        return return_str

    def __setitem__(self,key,value):
        self.db.update({key: value}, self.data.type == self.datatype)

    def __str__(self):
        returndata = self.db.search(self.data.type == self.datatype)
        if returndata:
            return str(returndata[0])
        else:
            return str({})