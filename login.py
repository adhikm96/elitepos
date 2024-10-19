from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.factory import Factory
import hashlib, binascii, os
import settings
from pos_helper import pconn
from pony.orm import *


class Login(Screen):
	def submit(self):
		if not self.ids.user_name.text:
			Factory.warning_pop("Please Enter User name").open()
		elif not self.ids.password.text:
			Factory.warning_pop("Please Enter Passward").open()
		else:
			res = pconn.get_single_dbrecord_wpk('User', 'name', self.ids.user_name.text)
			with db_session:
				if res:
					for i in res:
						if self.verify_password(i.password, self.ids.password.text):
							self.manager.current= 'main_page'
						else:
							self.ids.password.text = ""
							Factory.warning_pop("Password does not match ").open()
							
				else:
					self.ids.user_name.text = ""
					Factory.warning_pop("Unknown User").open()

	def verify_password(self, stored_password, provided_password):
	    """Verify a stored password against one provided by user"""
	    salt = stored_password[:64]
	    stored_password = stored_password[64:]
	    pwdhash = hashlib.pbkdf2_hmac('sha512', 
	                                  provided_password.encode('utf-8'), 
	                                  salt.encode('ascii'), 
	                                  100000)
	    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
	    return pwdhash == stored_password

