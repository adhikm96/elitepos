from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
import time

class Customer(Screen):
    customer_name = ObjectProperty()
    contact_number = ObjectProperty()
    contact_email = ObjectProperty()
    def cancel(self):
        self.customer_name.text = ""
        self.contact_number.text = ""
        self.contact_email.text = ""

    def save(self):
        pass

class CustomerGrid(GridLayout):
    customer_name = ObjectProperty()
    contact_number = ObjectProperty()
    contact_email = ObjectProperty()

class CustomerList(Screen):
	def on_pre_enter(self):
		self.cust.data = [{'customer_name': str('Customer'+' '+str(x)),'contact_number':str('12345'+str(x)),'contact_email':str('Customer'+str(x)+'@gmail.com')}
                        for x in range(50)]

class CustomerDropDown(DropDown):
    data = ['Customer 1','Customer 2','Customer 3']
    def __init__(self, **kwargs):
        super(CustomerDropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)