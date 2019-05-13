import settings
from pony import orm
from pony.orm import *
from models import db, base
from models.base import Customer

baseCls = base.__dict__

class PosHelper:
    def __init__(self):
        db.bind(**settings.db_params)
        db.generate_mapping(create_tables=True)
    
    @db_session
    def get_dbdata(self, namecls):
        return baseCls[namecls].select()
    
    @db_session
    def get_single_dbrecord(self, idx, namecls):
        # query = 'select {0} from {1} where id={2}'.format(fields, namecls, idx)
        # return baseCls[namecls].get_for_update(id=idx, nowait=True)
        return baseCls[namecls][idx]

    @db_session
    def update_single_dbrecord(self, idx, namecls, payload):
        record = baseCls[namecls][idx]
        try:  
            for e in payload.ids:
                setattr(record, e, payload.ids[e].text)
            commit()
            print "Record updated successfully."
            return "Success"
        except e:
            print e
            print "Failed to update"
            return "Error"

    @db_session
    def insert_single_dbrecord(self, namecls, payload):
        record = baseCls[namecls]()
        try:  
            for e in payload.ids:
                setattr(record, e, payload.ids[e].text)
            commit()
            print "Record created successfully."
            return "Success"
        except e:
            print e
            print "Failed to create"
            return "Error"

    @db_session
    def delete_single_dbrecord(self, namecls, idx):
        record = baseCls[namecls][idx]
        try:
            record.delete()
            print "Record deleted successfully."
            return "Success"
        except e:
            print e
            print "Failed to delete"
            return "Error"

pconn = PosHelper()