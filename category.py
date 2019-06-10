from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
import time

class Category(Screen):
    name = ObjectProperty()

    def cancel(self):
        self.ids.name.text = ""

    def save(self):
        pass


class CategoryGrid(GridLayout):
    name = ObjectProperty()

class CategoryList(Screen):
    def on_pre_enter(self):
        self.cat.data =  [{'name': str('Category'+' '+str(x))}
                        for x in range(50)]

class CategoryDropDown(DropDown):
    data = ['Category 1','Category 2','Category 3']
    def __init__(self, **kwargs):
        super(CategoryDropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)