from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.recycleview.views import RecycleDataViewBehavior
import time, settings
from pos_helper import pconn
from pony.orm import *

current_click_idx = ""

class Item(Screen):
    name = ObjectProperty()
    item_code = ObjectProperty()
    category = ObjectProperty()
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
                tax_data = [{'idx': idx, 'record_id': e.id, 'instance':'TaxItem', 'pclass': self, 'tax_type': e.tax.name, 'tax': int(e.tax.id), 'percent': e.percent if e.percent else 0, 'amount': e.amount if e.amount else 0 } for idx, e in enumerate(data.tax_items)]
                blank_rows = [{'idx': len(tax_data)+e, 'record_id': 0, 'instance':'TaxItem', 'pclass': self, 'tax_type':"", 'tax': 0, 'percent': 0, 'amount': 0 } for e in range(5-len(tax_data))]
                self.tax_items.data = tax_data + blank_rows
        else:
            self.ids.name.text = ""
            self.ids.item_code.text = ""
            self.tax_items.data = [{'idx': e, 'record_id': 0, 'instance':'TaxItem', 'pclass': self, 'tax_type':"", 'tax': "", 'percent': 0, 'amount': 0 } for e in range(5)]

    def cancel(self):
        self.ids.name.text = ""
        self.ids.item_code.text = ""

    def save(self):
        # raise ValueError(self.ids.tax_items.data)
        global current_click_idx
        payload = self
        if current_click_idx and current_click_idx != "":
            res = pconn.update_nested_dbrecord(current_click_idx, 'Item', payload, ["tax"], ["tax_type"])
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'item_list'
            else:
                pass
        else:
            res = pconn.insert_nested_dbrecord('Item', payload, ["tax"], ["tax_type"])
            if res == "Success":
                self.manager.current= 'item_list'
            else:
                pass


class ItemGrid(GridLayout):
    idx = ObjectProperty()
    name = ObjectProperty()
    item_code = ObjectProperty()
    category = ObjectProperty()
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
            self.itm.data = [{'idx': str(x.id), 'name': str(x.name),'item_code':str(x.item_code)}
                            for x in data]

class ItemCodeDropDown(DropDown):
    data = ['434343','7863313','2137878']
    def __init__(self, **kwargs):
        super(ItemCodeDropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)


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