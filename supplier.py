from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
import time

class Supplier(Screen):
    supplier_name = ObjectProperty()
    address = ObjectProperty()
    tax_id_gst_no = ObjectProperty()
    contact_number = ObjectProperty()
    email = ObjectProperty()

    def cancel(self):
        self.supplier_name.text = ""
        self.address.text = ""
        self.tax_id_gst_no.text = ""
        self.contact_number.text = ""
        self.email.text = ""

    def save(self):
        pass

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
