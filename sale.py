from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
import time
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem

class PaymentPopup(Popup):
    tm = ObjectProperty()
    time = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(PaymentPopup,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)

class SaleTab(TabbedPanel):
    pass


class Sale(Screen):
    tm = ObjectProperty()
    def on_pre_enter(self):
        self.sal.data = [{'item': str('item'+' '+str(x)),'rate':str(10+x),'dis':'5','amt':str(10+x-5)}
                        for x in range(50)]
        #raise ValueError(self.rv.data)
        
    time = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(Sale,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.tm = str(self.time)

    def show_popup(self):
        p = PaymentPopup(title='Payment',size_hint=(None, None), 
            size=(800, 600),auto_dismiss= False)
        p.open()

    def add_screen(self):
        tp=SaleTab()
        panel = TabbedPanelItem()
        tp.add_widget(panel)

class SaleTable(GridLayout):
    item = ObjectProperty()
    rate = ObjectProperty()
    dis = ObjectProperty()
    amt = ObjectProperty()

class SaleGrid(GridLayout):
    customer_name = ObjectProperty()
    total = ObjectProperty()
    

class SaleList(Screen):
    def on_pre_enter(self):
        self.sallist.data = [{'customer_name': str('Customer'+' '+str(x)),'total':str('123'+str(x))}
                        for x in range(50)]

