from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.factory import Factory
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import settings
from pos_helper import pconn
from pony.orm import *

current_click_idx = ""
class Category(Screen):
    name = ObjectProperty()
    delete_button_text = ObjectProperty()
    update_button_text = ObjectProperty()
    
    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'Category')
            if data:
                self.ids.name.text = str(data.name)
                self.delete_button_text = "Delete"
                self.update_button_text = "Update"
        else:
            self.ids.name.text = ""
            self.delete_button_text = "Cancel"
            self.update_button_text = "Save"

    def cancel(self):
        global current_click_idx
        if current_click_idx:
            res = pconn.delete_single_dbrecord( 'Category',current_click_idx)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'category_list'
            else:
                pass
        else:
            self.ids.name.text = ""
    
    def save(self):
        if not self.ids.name.text:
            Factory.warning_pop("Please enter Category name").open()
        else:
            global current_click_idx
            payload = self
            if current_click_idx and current_click_idx != "":
                res = pconn.update_single_dbrecord(current_click_idx, 'Category', payload)
                if res == "Success":
                    current_click_idx = ""
                    self.manager.current= 'category_list'
                else:
                    pass
            else:
                res = pconn.insert_single_dbrecord('Category', payload)
                if res == "Success":
                    self.manager.current= 'category_list'
                else:
                    pass

class CategoryGrid(GridLayout):
    idx = ObjectProperty()
    name = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'category'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")

class CategoryList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('Category')   
        with db_session:
            self.cat.data = [{'idx': str(x.id), 'name': str(x.name)}
                            for x in data]

    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""

class CategoryDropDown(DropDown):
    data = []
    imparent = ObjectProperty()

    def __init__(self, imparent, **kwargs):
        super(CategoryDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.data = pconn.cusrtomer_supplier_query_search('Category', imparent.ids.category.text)
        self.add_buttons()

    def set_category(self, cur):
        self.select(cur.text)
        self.imparent.ids.category.text = str(cur.text)

    def add_buttons(self):
        with db_session:
            for index, e in  enumerate(self.data):
                btn = Factory.Custom_drop_down_button(text='%s' % str(e.name),text_size = self.imparent.ids.category.size)
                btn.bind(on_release=self.set_category)
                self.add_widget(btn)
            self.imparent.category_dp_widget = self