from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
import time

class Item(Screen):
    #tax_data = ListProperty([{}, {}, {},{}, {}])
    item_name = ObjectProperty()
    item_code = ObjectProperty()
    category = ObjectProperty()

    def cancel(self):
        self.item_name.text = ""
        self.item_code.text = ""

    def save(self):
        pass

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

