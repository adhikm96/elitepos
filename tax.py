from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
import time, settings
from pos_helper import pconn
from pony.orm import *

current_click_idx = ""

class Tax(Screen):
    name = ObjectProperty()
    percent = ObjectProperty()
    tax_type = ObjectProperty()

    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'Tax')
            if data:
                self.ids.name.text = str(data.name)
                self.ids.tax_type.text = str(data.tax_type)
                self.ids.percent.text = str(data.percent)
        else:
            self.ids.name.text = ""
            self.ids.tax_type.text = "Select"
            self.ids.percent.text = ""

    def cancel(self):
        self.ids.name.text = ""
        self.ids.tax_type.text = "Select"
        self.ids.percent.text = ""
        global current_click_idx
        current_click_idx = ""

    def save(self):
        global current_click_idx
        payload = self
        if current_click_idx and current_click_idx != "":
            res = pconn.update_single_dbrecord(current_click_idx, 'Tax', payload)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'tax_list'
            else:
                pass
        else:
            res = pconn.insert_single_dbrecord('Tax', payload)
            if res == "Success":
                self.manager.current= 'tax_list'
            else:
                pass


class TaxGrid(GridLayout):
    idx = ObjectProperty()
    name = ObjectProperty()
    tax_type = ObjectProperty()
    percent = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'tax'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")


class TaxList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('Tax')   
        with db_session:
            self.tx.data = [{'idx': str(x.id), 'name': str(x.name),'tax_type':str(x.tax_type),'percent':str(x.percent)}
                            for x in data]

class TaxTypeDropDown(DropDown):
    tax_type = ObjectProperty()

    data = ['On Total','Actual']

    def __init__(self, **kwargs):
        super(TaxTypeDropDown, self).__init__(**kwargs)
        self.add_buttons()
        # raise ValueError(self.tax_type)
        

    def add_buttons(self):
        for i in self.data:
            btn = Button(text='%s' % i, size_hint_y=None, height=44)
            # btn.bind(on_release=lambda btn: self.select(btn.text))
            btn.value = i
            btn.bind(on_release=self.set_tax)
            self.add_widget(btn)

    def set_tax(self, cur):
        self.tax_type = cur.value
        self.select(cur.text)

class TaxDropDown(DropDown):
    data =  pconn.get_dbdata('Tax')
    imparent = ObjectProperty()

    def __init__(self, imparent, **kwargs):
        super(TaxDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def set_tax(self, cur):
        self.imparent.tax = cur.value.id
        self.select(cur.text)
        self.imparent.ids.tax_type.text = cur.text
        self.imparent.update_data()

    def add_buttons(self):
        with db_session:
            for i in self.data:
                btn_text = i.name
                btn = Button(text='%s' % i.name, size_hint_y=None, height=44 )
                btn.value = i
                # btn.cur_pclass = cur_pclass
                btn.bind(on_release=self.set_tax)
                self.add_widget(btn)