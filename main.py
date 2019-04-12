import kivy
from kivy.app import App
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
from kivy.uix.listview import ListItemButton
from string import ascii_lowercase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import time

class Main_Page(Screen):
	pass

class Customer_List(Screen):
	pass

class Customer(Screen):
    rv_data = ListProperty([{'text': 'A', 'value':'1'}, {'text': 'B','value':'2'}, {'text': 'C','value':'3'}])
    customer_name = ObjectProperty()
    contact_number = ObjectProperty()
    contact_email = ObjectProperty()
    customer_name_list = ObjectProperty()
    def cancel(self):
        self.customer_name.text = ""
        self.contact_number.text = ""
        self.contact_email.text = ""

    def save(self):
        if not self.customer_name.text=="": 
            # Get the student name from the TextInputs
            c_name = self.customer_name.text
            # Add the student to the ListView
            self.customer_name_list.adapter.data.extend([c_name ])
            # Reset the ListView
            self.customer_name_list._trigger_reset_populate()
            

class Supplier(Screen):
    supplier_name = ObjectProperty()
    address = ObjectProperty()
    tax_id_gst_no = ObjectProperty()
    contact_number = ObjectProperty()
    email = ObjectProperty()

    def cancel(self):
        self.supplier_name.text = ""
        self.address.text = ""
        self.tax_id_gst_no.text = ""
        self.contact_number.text = ""
        self.email.text = ""

    def save(self):
        pass

class Category_DropDown(DropDown):
    data = ['Category 1','Category 2','Category 3']
    def __init__(self, **kwargs):
        super(Category_DropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

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

class Tax_Type_DropDown(DropDown):
    data = ['On Total','Actual']
    def __init__(self, **kwargs):
        super(Tax_Type_DropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class Taxes(Screen):
    tax_name = ObjectProperty()
    percentage = ObjectProperty()

    def cancel(self):
        self.tax_name.text = ""
        self.percentage.text = ""
        

    def save(self):
        pass


class Customer_DropDown(DropDown):
    data = ['Customer 1','Customer 2','Customer 3']
    def __init__(self, **kwargs):
        super(Customer_DropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)



class Sales(Screen):
    tm = ObjectProperty()
    def on_pre_enter(self):
        self.sal.data = [{'item': str('item'+' '+str(x)),'rate':str(10+x),'dis':'5','amt':str(10+x-5)}
                        for x in range(50)]
        #raise ValueError(self.rv.data)
        
    time = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(Sales,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)

class SalesTable(GridLayout):
    item = ObjectProperty()
    rate = ObjectProperty()
    dis = ObjectProperty()
    amt = ObjectProperty()


class Supplier_DropDown(DropDown):
    data = ['Supplier 1','Supplier 2','Supplier 3']
    def __init__(self, **kwargs):
        super(Supplier_DropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class Purchase(Screen):
    tm = ObjectProperty()
    def on_pre_enter(self):
        self.pur.data = [{'item': str('item'+' '+str(x)),'rate':str(10+x),'dis':'5','amt':str(10+x-5)}
                        for x in range(50)]

    time = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(Purchase,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)

class PurchaseTable(GridLayout):
    item = ObjectProperty()
    rate = ObjectProperty()
    dis = ObjectProperty()
    amt = ObjectProperty()

class Item_Code_DropDown(DropDown):
    data = ['434343','7863313','2137878']
    def __init__(self, **kwargs):
        super(Item_Code_DropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)


class Stock(Screen):
    tm = ObjectProperty()
    time = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(Stock,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)

class Payment_Type_DropDown(DropDown):
    data = ['Pay','Receive']
    def __init__(self, **kwargs):
        super(Payment_Type_DropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class Payment_Mode_DropDown(DropDown):
    data = ['Cash','Card','Credit']
    def __init__(self, **kwargs):
        super(Payment_Mode_DropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)


class Payment(Screen):
    tm = ObjectProperty()
    transaction_ref = ObjectProperty()
    card_four_digit = ObjectProperty()
    amount = ObjectProperty()

    def cancel(self):
        self.transaction_ref.text = ""
        self.card_four_digit.text = ""
        self.amount.text = ""

    def save(self):
        pass

    time = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(Payment,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)


class Manager(ScreenManager):
	main_page = ObjectProperty(None)
	customer_list = ObjectProperty(None)
	customer = ObjectProperty(None)
	supplier = ObjectProperty(None)
	item = ObjectProperty(None)
	taxes = ObjectProperty(None)
	sales = ObjectProperty(None)
	purchase = ObjectProperty(None)
	stock = ObjectProperty(None)
	payment = ObjectProperty(None)

class ScreensApp(App):
    def build(self):
        return Manager()
 
SA =  ScreensApp()
 
SA.run()
