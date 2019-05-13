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
    tax_type = ObjectProperty()

    def cancel(self):
        self.tax_name.text = ""
        self.percentage.text = ""
        

    def save(self):
        pass

class TaxGrid(GridLayout):
    tax_name = ObjectProperty()
    tax_type = ObjectProperty()
    percentage = ObjectProperty()

class TaxList(Screen):
    def on_pre_enter(self):
        self.tx.data = [{'tax_name': str('Tax'+' '+str(x)),'tax_type':str('type'+' '+str(x)),'percentage':str(str(x))}
                        for x in range(50)]

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

