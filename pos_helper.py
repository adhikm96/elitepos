import settings
from pony import orm
from pony.orm import *
from models import db, base
from models.base import Customer

baseCls = base.__dict__

custom_validations = {
    "TaxItem" : {
        "primary": {
            "amount" : float,
            "percent" : float,
            "tax": int
        }        
    },
    "failedValidations": {
        "<type 'float'>" : 0.00,
        "<type 'int'>" : 0,
        "<type 'basestring'>": ""
    }
}

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
    def update_nested_dbrecord(self, idx, namecls, payload, mandatory_row_cols, to_ignore_row_cols):
        record = baseCls[namecls][idx]
        try:  
            for e in payload.ids:
                if payload.ids.has_key(e):
                    if hasattr(payload.ids[e], 'text'):
                        setattr(record, e, payload.ids[e].text)
                    elif hasattr(payload.ids[e], 'data'):     
                        for index, f in enumerate(payload.ids[e].data):
                            if f['record_id'] > 0:
                                nsdict = baseCls[f['instance']][f['record_id']]
                                if nsdict:
                                    for g in f:
                                        if hasattr(nsdict, g):
                                            setattr(nsdict, g, self.validate_against_custom_dict(f['instance'], g, f[g]))
                else:
                    if hasattr(payload.ids[e], 'text'):
                        rec_args[e] = ""
            rec_args = {}
            if namecls == "Item":
                rec_args['item_code'] = str(record.item_code)
            self.insert_new_children(namecls, idx, rec_args, payload, mandatory_row_cols, to_ignore_row_cols)
            commit()
            print "Record updated successfully."
            return "Success"
        except e:
            print e
            print "Failed to update"
            return "Error"

    @db_session
    def insert_single_dbrecord(self, namecls, payload):
        nxt = max(p.id for p in baseCls[namecls])
        nxt = nxt + 1 if nxt else 1
        try:
            rec_args = {}
            rec_args['id'] = nxt
            for e in payload.ids:
                    rec_args[e] = payload.ids[e].text if payload.ids.has_key(e) else ""
            print rec_args
            record = baseCls[namecls](**rec_args)
            # for e in payload.ids:
            #     setattr(record, e, payload.ids[e].text)
            commit()
            print "Record created successfully."
            return "Success"
        except e:
            print e
            print "Failed to create"
            return "Error"

    @db_session
    def insert_nested_dbrecord(self, namecls, payload, mandatory_row_cols, to_ignore_row_cols):
        nxt = max(p.id for p in baseCls[namecls])
        nxt = nxt + 1 if nxt else 1
        try:
            rec_args = {}
            rec_args['id'] = nxt
            for e in payload.ids:
                if payload.ids.has_key(e):
                    if hasattr(payload.ids[e], 'text'):
                        rec_args[e] = payload.ids[e].text or ""
                else:
                    if hasattr(payload.ids[e], 'text'):
                        rec_args[e] = ""

            record = baseCls[namecls](**rec_args)
            flush()
            self.insert_new_children(namecls, nxt, rec_args, payload, mandatory_row_cols, to_ignore_row_cols)
            commit()
            print "Record created successfully."
            return "Success"
        except e:
            print e
            print "Failed to create"
            return "Error"

    @db_session
    def insert_new_children(self, namecls, nxt, rec_args, payload, mandatory_row_cols, to_ignore_row_cols):
        for e in payload.ids:
            if payload.ids.has_key(e):
                if hasattr(payload.ids[e], 'data'):
                    rec_args[e] = []       
                    for index, f in enumerate(payload.ids[e].data):
                        if f['record_id'] == 0:
                            ndict = {}
                            blank_flag = True
                            print(f)
                            for g in f:
                                if g != 'idx' and g != 'pclass' and g != "instance" and g != "record_id" and g not in to_ignore_row_cols:
                                    if g in mandatory_row_cols and f[g]:
                                        blank_flag = False
                                    # setattr(ndict, g, f[g])
                                    # ndict.append(f[g])
                                    ndict[g] = self.validate_against_custom_dict(f['instance'], g, f[g])
                            if not blank_flag:
                                if namecls == 'Item':
                                    if isinstance(nxt, tuple):
                                        ndict[namecls.lower()] = nxt
                                    else:
                                        ndict[namecls.lower()] = (nxt,rec_args['item_code'])
                                else:
                                    ndict[namecls.lower()] = nxt
                                nsdict = baseCls[f['instance']]
                                print(ndict)
                                nsdict = nsdict(**ndict)
            else:
                if hasattr(payload.ids[e], 'data'):
                    rec_args[e] = []

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

    def validate_against_custom_dict(self, validClass, key, val):
        for e in custom_validations[validClass]["primary"]:
            if e == key:
                tempvar = custom_validations[validClass]["primary"][e]
                if isinstance(val, tempvar):
                    return val
                else:
                    return custom_validations["failedValidations"][str(tempvar)]

pconn = PosHelper()