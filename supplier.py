from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
import time
import time, settings
from pos_helper import pconn
from pony.orm import *

current_click_idx = ""

class Supplier(Screen):
    name = ObjectProperty()
    address = ObjectProperty()
    tax_no = ObjectProperty()
    contact_number = ObjectProperty()
    email_address = ObjectProperty()

    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'Supplier')
            if data:
                self.ids.name.text = str(data.name)
                self.ids.address.text = str(data.address)
                self.ids.tax_no.text = str(data.tax_no)
                self.ids.contact_number.text = str(data.contact_number)
                self.ids.email_address.text = str(data.email_address)
        else:
            self.ids.name.text = ""
            self.ids.address.text = ""
            self.ids.tax_no.text = ""
            self.ids.contact_number.text = ""
            self.ids.email_address.text = ""

    def cancel(self):
        self.ids.name.text = ""
        self.ids.address.text = ""
        self.ids.tax_no.text = ""
        self.ids.contact_number.text = ""
        self.ids.email_address.text = ""
        global current_click_idx
        current_click_idx = ""

    def save(self):
        global current_click_idx
        payload = self
        if current_click_idx and current_click_idx != "":
            res = pconn.update_single_dbrecord(current_click_idx, 'Supplier', payload)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'supplier_list'
                self.manager.transition = SlideTransition(direction="right")
            else:
                pass
        else:
            res = pconn.insert_single_dbrecord('Supplier', payload)
            if res == "Success":
                self.manager.current= 'supplier_list'
                self.manager.transition = SlideTransition(direction="right")
            else:
                pass


class SupplierGrid(GridLayout):
    idx = ObjectProperty()
    name = ObjectProperty()
    address = ObjectProperty()
    tax_no = ObjectProperty()
    contact_number = ObjectProperty()
    email_address = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'supplier'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="left")

class SupplierList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('Supplier')   
        with db_session:
            self.sup.data = [{'idx': str(x.id), 'name': str(x.name),'address':str(x.address),'contact_number':str(x.contact_number),'tax_no':str(x.tax_no),'email_address':str(x.email_address)}
                            for x in data]

class SupplierDropDown(DropDown):
    data = ['Supplier 1','Supplier 2','Supplier 3']
    def __init__(self, **kwargs):
        super(SupplierDropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)
