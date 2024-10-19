from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.factory import Factory
from kivy.uix.button import Button
import hashlib, binascii, os
from kivy.uix.dropdown import DropDown
import time, settings, datetime
from kivy.clock import Clock
from kivy.uix.button import Button
import time, settings
from pos_helper import pconn
from pony.orm import *

current_click_idx = ""

class User(Screen):
    name = ObjectProperty()
    password = ObjectProperty()
    email_address = ObjectProperty()
    delete_button_text = ObjectProperty()
    update_button_text = ObjectProperty()
    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'User')
            if data:
                self.ids.name.text = str(data.name)
                self.ids.password.text = ""
                self.ids.email_address.text = str(data.email_address)
                self.delete_button_text = "Delete"
                self.update_button_text = "Update"
        else:
            self.ids.name.text = ""
            self.ids.password.text = ""
            self.ids.email_address.text = ""
            self.delete_button_text = "Cancel"
            self.update_button_text = "Save"

    def cancel(self):
        global current_click_idx
        if current_click_idx:
            res = pconn.delete_single_dbrecord( 'User',current_click_idx)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'user_list'
            else:
                pass
        else:
            self.ids.name.text = ""
            self.ids.password.text = ""
            self.ids.email_address.text = ""
        

    def save(self):
        #raise ValueError(self.ids.password.text)
        if not self.ids.name.text:
            Factory.warning_pop("Please enter User name").open()
        elif self.ids.password.text == "":
            Factory.warning_pop("Please enter password").open()
        else:
            global current_click_idx
            res = pconn.get_single_dbrecord_wpk('User', 'name', self.ids.name.text)
            with db_session:
                if res and not current_click_idx:
                    Factory.warning_pop("User already exist please use another user name").open()
                else:
                    self.ids.password.text = self.hash_password(self.ids.password.text)
                    payload = self
                    if current_click_idx and current_click_idx != "":
                        res = pconn.update_single_dbrecord(current_click_idx, 'User', payload)
                        if res == "Success":
                            current_click_idx = ""
                            self.manager.current= 'user_list'
                        else:
                            pass
                    else:
                        res = pconn.insert_single_dbrecord('User', payload)
                        if res == "Success":
                            self.manager.current= 'user_list'
                        else:
                            pass

    def hash_password(self,password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                    salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

class UserGrid(GridLayout):
    idx = ObjectProperty()
    name = ObjectProperty()
    password = ObjectProperty()
    email_address = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'user'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")

    
class UserList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('User')   
        with db_session:
            self.cust.data = [{'idx': str(x.id), 'name': str(x.name),'password':str(x.password),'email_address':str(x.email_address)}
                            for x in data]

    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""


