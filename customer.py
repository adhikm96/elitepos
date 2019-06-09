from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
import time, settings
from pos_helper import pconn
from pony.orm import *

current_click_idx = ""

class Customer(Screen):
    name = ObjectProperty()
    contact_number = ObjectProperty()
    email_address = ObjectProperty()

    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'Customer')
            if data:
                self.ids.name.text = str(data.name)
                self.ids.contact_number.text = str(data.contact_number)
                self.ids.email_address.text = str(data.email_address)
        else:
            self.ids.name.text = ""
            self.ids.contact_number.text = ""
            self.ids.email_address.text = ""

    def cancel(self):
        self.ids.name.text = ""
        self.ids.contact_number.text = ""
        self.ids.email_address.text = ""

    def save(self):
        global current_click_idx
        payload = self
        if current_click_idx and current_click_idx != "":
            res = pconn.update_single_dbrecord(current_click_idx, 'Customer', payload)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'customer_list'
            else:
                pass
        else:
            res = pconn.insert_single_dbrecord('Customer', payload)
            if res == "Success":
                self.manager.current= 'customer_list'
            else:
                pass

class CustomerGrid(GridLayout):
    idx = ObjectProperty()
    name = ObjectProperty()
    contact_number = ObjectProperty()
    email_address = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'customer'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")

class CustomerList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('Customer')   
        with db_session:
            self.cust.data = [{'idx': str(x.id), 'name': str(x.name),'contact_number':str(x.contact_number),'email_address':str(x.email_address)}
                            for x in data]

class CustomerDropDown(DropDown):
    data =  pconn.get_dbdata('Customer')
    customer = ObjectProperty()
    def __init__(self, **kwargs):
        super(CustomerDropDown, self).__init__(**kwargs)
        self.add_buttons()

    def set_customer(self, cur):
        self.customer = cur.value
        self.select(cur.text)

    def add_buttons(self):
        with db_session:
            for i in self.data:
                btn_text = i.name
                btn = Button(text='%s' % i.name, size_hint_y=None, height=44 )
                btn.value = i
                btn.bind(on_release=self.set_customer)
                self.add_widget(btn)

    