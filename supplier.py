from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.clock import Clock
import time, settings, datetime
import time
import time, settings
from pos_helper import pconn
from pony.orm import *
import os

current_click_idx = ""

class Supplier(Screen):
    name = ObjectProperty()
    address = ObjectProperty()
    tax_no = ObjectProperty()
    contact_number = ObjectProperty()
    email_address = ObjectProperty()
    delete_button_text = ObjectProperty()
    update_button_text = ObjectProperty()

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
                self.delete_button_text = "Delete"
                self.update_button_text = "Update"
        else:
            self.ids.name.text = ""
            self.ids.address.text = ""
            self.ids.tax_no.text = ""
            self.ids.contact_number.text = ""
            self.ids.email_address.text = ""
            self.delete_button_text = "Cancel"
            self.update_button_text = "Save"

    def cancel(self):
        global current_click_idx
        if current_click_idx:
            res = pconn.delete_single_dbrecord( 'Supplier',current_click_idx)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'supplier_list'
            else:
                pass
        else:
            self.ids.name.text = ""
            self.ids.address.text = ""
            self.ids.tax_no.text = ""
            self.ids.contact_number.text = ""
            self.ids.email_address.text = ""

    def save(self):
        if not self.ids.name.text:
            Factory.warning_pop("Please enter Supplier name").open()
        else:
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

    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""
class SupplierDropDown(DropDown):
    data = []
    imparent = ObjectProperty()

    def __init__(self, imparent, **kwargs):
        super(SupplierDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.data = pconn.cusrtomer_supplier_query_search('Supplier', imparent.ids.supplier_name.text)
        self.add_buttons()

    def set_supplier(self, cur):
        self.imparent.supplier = cur.value
        self.imparent.supplier_selected = cur.text
        self.select(cur.text)
        self.imparent.ids.supplier_name.text = str(cur.text)

    def add_buttons(self):
        with db_session:
            for index, e in  enumerate(self.data):
                btn = Factory.Custom_drop_down_button(text='%s' % str(e.name), text_size = self.imparent.ids.supplier_name.size)
                btn.value = e.id
                btn.bind(on_release=self.set_supplier)
                self.add_widget(btn)
        self.imparent.supplier_dp_widget = self

class SearchSupplierDropDown(DropDown):
    data = []
    imparent = ObjectProperty()

    def __init__(self, imparent, **kwargs):
        super(SearchSupplierDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.data = pconn.cusrtomer_supplier_query_search('Supplier', imparent.ids.selected_supplier.text)
        self.add_buttons()

    def set_supplier(self, cur):
        self.imparent.supplier_selected = cur.text
        self.select(cur.text)
        self.imparent.ids.selected_supplier.text = str(cur.text)
        if not self.imparent.ids.selected_date.text:
            data = pconn.get_search_dbrecord_wpk("PurchaseInvoice", "supplier", cur.value)
            with db_session:
                if data:
                    self.imparent.purlist.data = [{'idx': str(x.id), 'supplier': str(x.supplier.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                            for x in data ]
                else:
                    self.imparent.purlist.data = []
        else:
            laDate = self.imparent.ids.selected_date.text
            datepicked = datetime.datetime.strptime(laDate, '%d.%m.%Y').strftime('%Y-%m-%d') 
            dategive = datetime.datetime.strptime(datepicked, '%Y-%m-%d').date()
            data = pconn.get_search_dbrecord_wpk_by_name_date("PurchaseInvoice","supplier",self.imparent.ids.selected_supplier.text, "invoice_date", dategive)
            with db_session:
                if data:
                    self.imparent.purlist.data = [{'idx': str(x.id), 'supplier': str(x.supplier.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                            for x in data ]
                else:
                    self.imparent.purlist.data = []

    def add_buttons(self):
        with db_session:
            for index, e in  enumerate(self.data):
                btn = Factory.Custom_drop_down_button(text='%s' % str(e.name), text_size = self.imparent.ids.selected_supplier.size)
                btn.bind(on_release=self.set_supplier)
                btn.value = e.id
                self.add_widget(btn)
        self.imparent.supplier_dp_widget = self