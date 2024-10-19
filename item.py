from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.factory import Factory
import json
from kivy.uix.recycleview.views import RecycleDataViewBehavior
import time, settings
from pos_helper import pconn
from pony.orm import *

current_click_idx = ""

class Item(Screen):
    name = ObjectProperty()
    item_code = ObjectProperty()
    valuation_rate = ObjectProperty()
    category = ObjectProperty()
    category_dp_widget = ObjectProperty()
    tax_items = []

    @db_session
    def on_pre_enter(self):  
        global current_click_idx
        print(current_click_idx)
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'Item')
            # raise ValueError(data.tax_items)
            if data:
                self.ids.name.text = str(data.name)
                self.ids.item_code.text = str(data.item_code)
                self.ids.valuation_rate.text = str(data.valuation_rate)
                tax_data = [{'idx': idx, 'record_id': e.id, 'instance':'TaxItem', 'pclass': self, 'tax_type': e.tax.name, 'tax': int(e.tax.id), 'percent': e.percent if e.percent else 0, 'amount': e.amount if e.amount else 0 } for idx, e in enumerate(data.tax_items)]
                blank_rows = [{'idx': len(tax_data)+e, 'record_id': 0, 'instance':'TaxItem', 'pclass': self, 'tax_type':"", 'tax': 0, 'percent': 0, 'amount': 0 } for e in range(5-len(tax_data))]
                self.tax_items.data = tax_data + blank_rows
        else:
            self.ids.name.text = ""
            self.ids.item_code.text = ""
            self.ids.valuation_rate.text = ""
            self.tax_items.data = [{'idx': e, 'record_id': 0, 'instance':'TaxItem', 'pclass': self, 'tax_type':"", 'tax': "", 'percent': 0, 'amount': 0 } for e in range(5)]

    
        
    def cancel(self):
        self.ids.name.text = ""
        self.ids.item_code.text = ""
        self.ids.valuation_rate.text = ""
        self.tax_items.data = []
        global current_click_idx
    	current_click_idx = ""

    def save(self):
        #raise ValueError(self.ids.tax_items.data)
        global current_click_idx
        payload = self
        if current_click_idx and current_click_idx != "":
            res = pconn.update_nested_dbrecord(current_click_idx, 'Item', payload, {"0":[],"TaxItem":["tax"]}, {"0":[],"TaxItem":["tax_type"]})
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'item_list'
            else:
                pass
        else:
            res = pconn.insert_nested_dbrecord('Item', payload,  {"0":[],"TaxItem":["tax"]}, {"0":[],"TaxItem":["tax_type"]})
            if res == "Success":
                self.manager.current= 'item_list'
            else:
                pass

    def on_category_input(self):
        if self.category_dp_widget:
            self.category_dp_widget.clear_widgets()
        if self.ids.category.text:
            Factory.CategoryDropDown(self).open(self.ids.category)

class ItemGrid(GridLayout):
    idx = ObjectProperty()
    name = ObjectProperty()
    item_code = ObjectProperty()
    category = ObjectProperty()
    valuation_rate = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = (self.idx, self.item_code)
        self.parent.parent.parent.parent.parent.parent.manager.current= 'item'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")
        
    

class ItemList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('Item')   
        with db_session:
            self.itm.data = [{'idx': str(x.id), 'name': str(x.name),'item_code':str(x.item_code),'valuation_rate':str(x.valuation_rate) if x.valuation_rate else "" }
                            for x in data ]
    	
    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""
class SaleItemCodeDropDown(DropDown):
    data = []
    imparent = ObjectProperty()
    def __init__(self, imparent, **kwargs):
        super(SaleItemCodeDropDown, self).__init__(**kwargs)
        self.background_color= (1,1,1, 1)
        self.imparent = imparent
        self.data = pconn.query_search('Item', imparent.ids.item_code.text)
        self.add_buttons()


    def set_item_code(self, cur):
        qty  = pconn.get_stock_quantity('StockLedger', cur.itm_code)
        with db_session:
            if qty <= 0:
                Factory.warning_pop("Item have no Stock").open()
                self.imparent.ids.item_code.text = ""
            else:
                self.imparent.ids.item_code.text = cur.text
                self.select(cur.text)
                self.imparent.ids.sales_invoice_items.data.append({'idx':  len(self.imparent.ids.sales_invoice_items.data),'record_id': 0,
                                                      'instance':'SalesInvoiceItem','pclass': self.imparent,'item':cur.value,'item_code': cur.itm_code,
                                                      'rate':str(cur.rate if cur.rate else 0 ),'quantity': "1" ,
                                                      'discount': 0 , 'discount_percent': 0 ,'tax_string': json.dumps(cur.tax_info) })
                self.imparent.ids.item_code.text = ""
                self.imparent.recalculate_taxes(cur.tax_info, len(self.imparent.ids.sales_invoice_items.data)-1, cur.itm_code, cur.rate)

    def add_buttons(self):
        with db_session:
            for index, e in enumerate(self.data):
                btn = Factory.Custom_drop_down_button(text='{} - {}'.format(str(e.item_code), str(e.name)),
                 text_size = self.imparent.ids.item_code.size)
                btn.bind(on_release=self.set_item_code)
                btn.itm_code = e.item_code
                btn.value = (e.id,e.item_code)
                btn.tax_info = {e.item_code: [p.to_dict() for p in e.tax_items]}
                btn.rate = e.valuation_rate if e.valuation_rate else 0.0
                self.add_widget(btn)
        self.imparent.item_dp_widget = self


class PurchaseItemCodeDropDown(DropDown):
    data = []
    imparent = ObjectProperty()
    def __init__(self, imparent, **kwargs):
        super(PurchaseItemCodeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.data = pconn.query_search('Item', imparent.ids.item_code.text)
        # print self.data
        self.add_buttons()



    def set_item_code(self, cur):
        self.imparent.ids.item_code.text = cur.text
        self.select(cur.text)
        self.imparent.ids.purchase_invoice_items.data.append({'idx':  len(self.imparent.ids.purchase_invoice_items.data),'record_id': 0,
                                              'instance':'PurchaseInvoiceItem','pclass': self.imparent,'item':cur.value,
                                              'item_code': cur.itm_code,'rate':str(cur.rate),'amount':str(cur.rate),'quantity': "1",
                                              'discount': 0 , 'discount_percent': 0, 'tax_string': json.dumps(cur.tax_info) })
        self.imparent.ids.item_code.text = ""
        self.imparent.recalculate_taxes(cur.tax_info, len(self.imparent.ids.purchase_invoice_items.data)-1, cur.itm_code, cur.rate)

    def add_buttons(self):
        with db_session:
            for index, e in enumerate(self.data):
                btn = Factory.Custom_drop_down_button(text='{} - {}'.format(str(e.item_code), str(e.name)),
                 text_size = self.imparent.ids.item_code.size)
                btn.bind(on_release=self.set_item_code)
                btn.itm_code = e.item_code
                btn.value = (e.id,e.item_code)
                btn.tax_info = {e.item_code: [p.to_dict() for p in e.tax_items]}
                btn.rate = e.valuation_rate if e.valuation_rate else 0.0
                self.add_widget(btn)
        self.imparent.item_dp_widget = self

class ItemCodeDropDown(DropDown):
    data = []
    imparent = ObjectProperty()
    def __init__(self, imparent, **kwargs):
        super(ItemCodeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.data = pconn.query_search('Item', imparent.ids.item_code.text)
        self.add_buttons()


    def set_item_code(self, cur):
        self.imparent.item = cur.value
        self.imparent.ids.item_code.text = cur.text
        self.select(cur.text)
        qty = pconn.get_stock_quantity('StockLedger', cur.itm_code)
        with db_session:
            self.imparent.ids.stock_reconciliation_items.data.append({'idx':  len(self.imparent.ids.stock_reconciliation_items.data),'record_id': 0,
                                              'instance':'StockReconciliationItem','pclass': self.imparent,'item':cur.value,
                                              'item_code': cur.itm_code,"current_stock": float(qty if qty else 0), "revised_stock": float(0)})
            self.imparent.ids.item_code.text = ""

    def add_buttons(self):
        with db_session:
            for index, e in enumerate(self.data):
                btn = Factory.Custom_drop_down_button(text='{} - {}'.format(str(e.item_code), str(e.name)),
                 text_size = self.imparent.ids.item_code.size)
                btn.bind(on_release=self.set_item_code)
                btn.itm_code = e.item_code
                btn.value = (e.id,e.item_code)
                self.add_widget(btn)
        self.imparent.item_dp_widget = self


class CustomTaxTable(RecycleDataViewBehavior, GridLayout):
    tax = ObjectProperty()
    tax_type = ObjectProperty()
    percent = NumericProperty()
    amount = NumericProperty()
    idx = None
    pclass = ObjectProperty()
    instance = StringProperty()
    record_id = NumericProperty()

    # def __init__(self, **kwargs):
    #     super(CustomTaxTable, self).__init__(**kwargs)
    #     print(self.sobject)

    def __getitem__(self, item):
        return getattr(self, item)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.idx = data['idx']
        self.pclass = data['pclass']
        self.tax = data['tax']
        return super(CustomTaxTable, self).refresh_view_attrs(
            rv, index, data)

    def on_release(self):
        Factory.TaxDropDown(self).open(self.ids.tax_type)

    def update_data(self):
        for e in self.ids:
            setattr(self, e, self.ids[e].text)
        for e in self.pclass.ids.tax_items.data[self.idx]:
            if e != "idx" and e != "pclass" and e != "instance" and e != "record_id":
                self.pclass.ids.tax_items.data[self.idx][e] = self[e]
        print("updated {}".format(self.idx))