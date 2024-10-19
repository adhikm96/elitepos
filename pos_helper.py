import settings, re, datetime
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
    "SalesInvoiceItem": {
        "primary": {
            "item" : tuple,
            "rate" : float,
            "discount" : float,
            "discount_percent" : float,
            "amount": float,
            "quantity": int,
            "tax_string": basestring,
            "item_code": basestring
        }
    },
    "PurchaseInvoiceItem": {
        "primary": {
            "item" : tuple,
            "rate" : float,
            "discount" : float,
            "discount_percent" : float,
            "amount": float,
            "tax_string": basestring,
            "quantity": int,
            "item_code": basestring
        }
    },
    "Payment": {
        "primary": {
            "transaction_ref" : basestring,
            "payment_type" : basestring,
            "mode_of_payment" : basestring,
            "card_four_digits": int,
            "amount": float,
            "p_date": datetime.date,
            "p_time": datetime.time
        }
    },
    "StockLedger": {
        "primary": {
            "item": tuple,
            "sl_date": datetime.date,
            "sl_time": datetime.time,
            "quantity": int
        }
    },
    "StockReconciliationItem": {
        "primary": {
            "item" : tuple,
            "item_code": basestring,
            "current_stock": float,
            "revised_stock": float
        }
    },

    "PaymentLedger": {
        "primary": {
            "account" : int,
            "debit": float,
            "credit": float,
            "amount": float,
            "pl_date": datetime.date,
            "pl_time": datetime.time
        }
    },

    "failedValidations": {
        "<type 'float'>" : 0.00,
        "<type 'int'>" : 0,
        "<type 'basestring'>": "",
        "<type 'datetime.date'>": "null",
        "<type 'datetime.time'>": "null"
    }
}

class PosHelper:
    def __init__(self):
        db.bind(**settings.db_params)
        db.generate_mapping(create_tables=True)
    
    @db_session
    def query_search(self, namecls, query):
        return baseCls[namecls].select(lambda e: e.item_code.startswith(query) or e.name.startswith(query) )
        # return select()

    @db_session
    def get_single_dbrecord_wpk(self, namecls, key_name, query):
        return baseCls[namecls].select(lambda e: getattr(e, key_name) == query)

    @db_session
    def get_search_dbrecord_wpk(self, namecls, key_name, query):
        return baseCls[namecls].select(lambda e: getattr(e, key_name).id == query)

    @db_session
    def get_search_dbrecord_wpk_by_name_date(self, namecls, key_name, idquery, key_date, datequery):
        return baseCls[namecls].select(lambda e: getattr(e, key_name).name == idquery and getattr(e, key_date) == datequery )

    @db_session
    def get_stock_quantity(self, namecls, key_name):
        return sum(e.quantity for e in baseCls[namecls] if e.item.item_code == key_name)

    @db_session
    def cusrtomer_supplier_query_search(self, namecls, query):
        return baseCls[namecls].select(lambda e: e.name.startswith(query))
        # return select()

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
                if payload.ids.has_key(e) and e not in to_ignore_row_cols["0"]:
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
                # else:
                #     if hasattr(payload.ids[e], 'text'):
                #         rec_args[e] = ""
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
            record = baseCls[namecls](**rec_args)
            # for e in payload.ids:
            #     setattr(record, e, payload.ids[e].text)
            print "Record created successfully."
            return "Success"
        except e:
            print e
            print "Failed to create"
            return "Error"

    @db_session
    def insert_nested_dbrecord(self, namecls, payload, mandatory_row_cols, to_ignore_row_cols, extra_children=[]):
        nxt = max(p.id for p in baseCls[namecls]) 
        nxt = nxt + 1 if nxt else 1
        try:
            rec_args = {}
            rec_args['id'] = nxt
            for e in payload.ids:
                if payload.ids.has_key(e) and e not in to_ignore_row_cols["0"]:
                    if hasattr(payload.ids[e], 'text'):
                        rec_args[e] = payload.ids[e].text or ""
                elif e not in to_ignore_row_cols["0"]:
                    if hasattr(payload.ids[e], 'text'):
                        rec_args[e] = ""
            record = baseCls[namecls](**rec_args)
            flush()
            self.insert_new_children(namecls, nxt, rec_args, payload, mandatory_row_cols, to_ignore_row_cols)
            if len(extra_children)>0:
                self.insert_extra_children(namecls, nxt, payload, extra_children)
            commit()
            print "Record created successfully."
            return "Success"
        except e:
            print e
            print "Failed to create"
            return "Error"

    @db_session
    def insert_new_children(self, namecls, nxt, rec_args, payload, mandatory_row_cols, to_ignore_row_cols):
        noc = 1
        for e in payload.ids:
            if payload.ids.has_key(e):
                print(e)
                if hasattr(payload.ids[e], 'data'):
                    print(e)
                    rec_args[e] = []       
                    for index, f in enumerate(payload.ids[e].data):
                        if f['record_id'] == 0:
                            ndict = {}
                            blank_flag = True
                            for g in f:
                                if g != 'idx' and g != 'pclass' and g != "instance" and g != "record_id" and g not in to_ignore_row_cols[f['instance']]:
                                    if g in mandatory_row_cols[f['instance']] and f[g]:
                                        blank_flag = False
                                    # setattr(ndict, g, f[g])
                                    # ndict.append(f[g])
                                    ndict[g] = self.validate_against_custom_dict(f['instance'], g, f[g])
                            if not blank_flag:
                                if namecls == 'Item':
                                    if isinstance(nxt, tuple):
                                        ndict[self.convert_to_snake(namecls)] = nxt
                                    else:
                                        ndict[self.convert_to_snake(namecls)] = (nxt,rec_args['item_code'])
                                else:
                                    ndict[self.convert_to_snake(namecls)] = nxt
                                nsdict = baseCls[f['instance']]
                                print("Child Record......................")
                                print(ndict)
                                nsdict = nsdict(**ndict)
                    print(noc)
                    noc = noc + 1
            else:
                if hasattr(payload.ids[e], 'data'):
                    rec_args[e] = []

    @db_session
    def insert_extra_children(self, namecls, nxt, payload, extra_children):
        for e in extra_children:
            cur_rec = getattr(payload, e) 
            if len(cur_rec) > 0:
                print(e)
                for index, f in enumerate(cur_rec):
                    if f['record_id'] == 0:
                        ndict = {}
                        blank_flag = True
                        for g in f:
                            if g != 'idx' and g != 'pclass' and g != "instance" and g != "record_id":
                                if f[g]:
                                    blank_flag = False
                                # setattr(ndict, g, f[g])
                                # ndict.append(f[g])
                                ndict[g] = self.validate_against_custom_dict(f['instance'], g, f[g])
                        if not blank_flag:
                            ndict["transaction_ref"] = str(nxt)
                            ndict["transaction_doc"] = namecls
                            nsdict = baseCls[f['instance']]
                            print("Child Extra Record......................")
                            print(ndict)
                            nsdict = nsdict(**ndict)

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

    def convert_to_snake(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

pconn = PosHelper()