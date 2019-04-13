from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
import time

class Tax(Screen):
    tax_name = ObjectProperty()
    percentage = ObjectProperty()

    def cancel(self):
        self.tax_name.text = ""
        self.percentage.text = ""
        

    def save(self):
        pass


class TaxTypeDropDown(DropDown):
    data = ['On Total','Actual']
    def __init__(self, **kwargs):
        super(TaxTypeDropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

