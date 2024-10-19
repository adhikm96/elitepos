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
class Account(Screen):
    account_name = ObjectProperty()
    account_type = ObjectProperty()
    activity = ObjectProperty()
    delete_button_text = ObjectProperty()
    update_button_text = ObjectProperty()

    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'Account')
            if data:
            	self.ids.account_name.text = str(data.account_name)
            	self.ids.account_type.text = str(data.account_type)
            	self.ids.activity.text = str(data.activity)
                self.delete_button_text = "Delete"
                self.update_button_text = "Update"
        else:
            self.ids.account_name.text = ""
            self.ids.account_type.text = "Select"
            self.ids.activity.text = "Select"
            self.delete_button_text = "Cancel"
            self.update_button_text = "Save"

    def cancel(self):
        global current_click_idx
        if current_click_idx:
            res = pconn.delete_single_dbrecord( 'Account',current_click_idx)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'account_list'
            else:
                pass
        else:
            self.ids.account_name.text = ""
            self.ids.account_type.text = "Select"
            self.ids.activity.text = "Select"
    
    def save(self):
        print "test"
        if not self.ids.account_name.text:
            Factory.warning_pop("Please enter Account name").open()
        else:
            global current_click_idx
            res = pconn.get_single_dbrecord_wpk('Account', 'activity', self.ids.activity.text)
            with db_session:
                if res and not current_click_idx:
                    Factory.warning_pop("User already exist please use another user name").open()
                else:
                    payload = self
                    if current_click_idx and current_click_idx != "":
                        res = pconn.update_single_dbrecord(current_click_idx, 'Account', payload)
                        if res == "Success":
                            current_click_idx = ""
                            self.manager.current= 'account_list'
                        else:
                            pass
                    else:
                        res = pconn.insert_single_dbrecord('Account', payload)
                        if res == "Success":
                            self.manager.current= 'account_list'
                        else:
                            pass


class AccountGrid(GridLayout):
    account_name = ObjectProperty()
    account_type = ObjectProperty()
    activity = ObjectProperty()
    idx = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'account'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")

class AccountList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('Account')   
        with db_session:
            self.act.data = [{'idx': str(x.id), 'account_name': str(x.account_name),'account_type': str(x.account_type),
            				'activity': str(x.activity)}for x in data]


    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""

class AccountTypeDropDown(DropDown):
    data = ['Debit','Asset','Divident','Expense','Credit','Equity','Liability','Revenue','Income']
    imparent = ObjectProperty()
    def __init__(self,imparent, **kwargs):
        super(AccountTypeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Factory.Custom_drop_down_button(text='%s' % self.data[index], text_size = self.imparent.ids.account_type.size)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class ActivityDropDown(DropDown):
    data = ['Sales','Inventory','Cash','Bank','Supplier-Credit','Customer-Credit','Discount','Tax']
    imparent = ObjectProperty()
    def __init__(self,imparent, **kwargs):
        super(ActivityDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Factory.Custom_drop_down_button(text='%s' % self.data[index], text_size = self.imparent.ids.activity.size)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)