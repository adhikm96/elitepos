import sys
from os import path
import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty,ListProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from KivyCalendar import DatePicker
from random import sample
from string import ascii_lowercase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import time

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
import elitepos.customer
import elitepos.supplier
import elitepos.item
import elitepos.tax
import elitepos.sale
import elitepos.purchase
import elitepos.stock
import elitepos.payment
import elitepos.category
import elitepos.account
import elitepos.login
import elitepos.user

from kivy.lang import Builder
Builder.load_file('ui/screens.kv')
Builder.load_file('ui/customer.kv')
Builder.load_file('ui/supplier.kv')
Builder.load_file('ui/item.kv')
Builder.load_file('ui/payment.kv')
Builder.load_file('ui/sale.kv')
Builder.load_file('ui/purchase.kv')
Builder.load_file('ui/tax.kv')
Builder.load_file('ui/stock.kv')
Builder.load_file('ui/category.kv')
Builder.load_file('ui/account.kv')
Builder.load_file('ui/login.kv')
Builder.load_file('ui/user.kv')
from pony import orm
import settings
from models import db


db.bind(**settings.db_params)
db.generate_mapping()

class MainPage(Screen):
	pass

class Manager(ScreenManager):    
	login = ObjectProperty(None)
	main_page = ObjectProperty(None)
	customer = ObjectProperty(None)
	customer_list = ObjectProperty()
	supplier = ObjectProperty(None)
	supplier_list = ObjectProperty()
	item = ObjectProperty(None)
	item_list = ObjectProperty()
	tax = ObjectProperty(None)
	tax_list = ObjectProperty()
	sale = ObjectProperty(None)
	sale_list = ObjectProperty()
	purchase = ObjectProperty(None)
	purchase_list = ObjectProperty()
	stock = ObjectProperty(None)
	stock_list = ObjectProperty()
	payment = ObjectProperty(None)
	payment_list = ObjectProperty()
	category_list = ObjectProperty(None)
	category = ObjectProperty()
	account_list = ObjectProperty(None)
	account = ObjectProperty()
	user_list = ObjectProperty(None)
	user = ObjectProperty()
    
class ScreensApp(App):
    def build(self):
    	Config.set('graphics', 'window_state', 'maximized')	
    	return Manager()
 
SA =  ScreensApp()
 
SA.run()
