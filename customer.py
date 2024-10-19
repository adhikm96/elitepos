from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
import time, settings, datetime
from kivy.clock import Clock
from kivy.uix.button import Button
import time, settings
from pos_helper import pconn
from pony.orm import *
import os

current_click_idx = ""

class Customer(Screen):
    name = ObjectProperty()
    contact_number = ObjectProperty()
    email_address = ObjectProperty()
    delete_button_text = ObjectProperty()
    update_button_text = ObjectProperty()

    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'Customer')
            if data:
                self.ids.name.text = str(data.name)
                self.ids.contact_number.text = str(data.contact_number)
                self.ids.email_address.text = str(data.email_address)
                self.delete_button_text = "Delete"
                self.update_button_text = "Update"
        else:
            self.ids.name.text = ""
            self.ids.contact_number.text = ""
            self.ids.email_address.text = ""
            self.delete_button_text = "Cancel"
            self.update_button_text = "Save"

    def cancel(self):
        global current_click_idx
        if current_click_idx:
            res = pconn.delete_single_dbrecord( 'Customer',current_click_idx)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'customer_list'
            else:
                pass
        else:
            self.ids.name.text = ""
            self.ids.contact_number.text = ""
            self.ids.email_address.text = ""
        

    def save(self):
        if not self.ids.name.text:
            Factory.warning_pop("Please enter Customer name").open()
        else:
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

    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""

class Custom_drop_down_button(Button):
    pass

class CustomerDropDown(DropDown):
    data = []
    imparent = ObjectProperty()

    def __init__(self, imparent, **kwargs):
        super(CustomerDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.data = pconn.cusrtomer_supplier_query_search('Customer', imparent.ids.customer_name.text)
        self.add_buttons()

    def set_customer(self, cur):
        self.imparent.customer = cur.value
        self.imparent.customer_selected = cur.text
        self.select(cur.text)
        self.imparent.ids.customer_name.text = str(cur.text)

    def add_buttons(self):
        with db_session:
            for index, e in  enumerate(self.data):
                btn = Custom_drop_down_button(text='%s' % str(e.name),text_size = self.imparent.ids.customer_name.size)
                btn.bind(on_release=self.set_customer)
                btn.value = e.id
                btn.bind(on_release=self.set_customer)
                self.add_widget(btn)
        self.imparent.customer_dp_widget = self

class SearchCustomerDropDown(DropDown):
    data = []
    imparent = ObjectProperty()

    def __init__(self, imparent, **kwargs):
        super(SearchCustomerDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.data = pconn.cusrtomer_supplier_query_search('Customer', imparent.ids.selected_customer.text)
        self.add_buttons()

    def set_customer(self, cur):
        self.imparent.customer_selected = cur.text
        self.select(cur.text)
        self.imparent.ids.selected_customer.text = str(cur.text)
        if not self.imparent.ids.selected_date.text:
            data = pconn.get_search_dbrecord_wpk("SalesInvoice", "customer", cur.value)
            with db_session:
                if data:
                    self.imparent.sallist.data = [{'idx': str(x.id), 'customer': str(x.customer.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                                for x in data ]
                else:
                    self.imparent.sallist.data = []
        else:
            laDate = self.imparent.ids.selected_date.text
            datepicked = datetime.datetime.strptime(laDate, '%d.%m.%Y').strftime('%Y-%m-%d') 
            dategive = datetime.datetime.strptime(datepicked, '%Y-%m-%d').date()
            data = pconn.get_search_dbrecord_wpk_by_name_date("SalesInvoice","customer",self.imparent.ids.selected_customer.text, "invoice_date", dategive)
            with db_session:
                if data:
                    self.imparent.sallist.data = [{'idx': str(x.id), 'customer': str(x.customer.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                                for x in data ]
                else:
                    self.imparent.sallist.data = []

    def add_buttons(self):
        with db_session:
            for index, e in  enumerate(self.data):
                btn = Custom_drop_down_button(text='%s' % str(e.name),
                 text_size = self.imparent.ids.selected_customer.size)
                btn.bind(on_release=self.set_customer)
                btn.value = e.id
                self.add_widget(btn)
        self.imparent.customer_dp_widget = self