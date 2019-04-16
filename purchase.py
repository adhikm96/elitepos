from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
import time
from sale import PaymentPopup

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

    def show_popup(self):
        p = PaymentPopup(title='Payment',size_hint=(None, None), 
            size=(800, 600),auto_dismiss= False)
        p.open()

class PurchaseTable(GridLayout):
    item = ObjectProperty()
    rate = ObjectProperty()
    dis = ObjectProperty()
    amt = ObjectProperty()

class PurchaseGrid(GridLayout):
    supplier_name = ObjectProperty()
    total = ObjectProperty()
    

class PurchaseList(Screen):
    def on_pre_enter(self):
        self.purlist.data = [{'supplier_name': str('Supplier'+' '+str(x)),'total':str('123'+str(x))}
                        for x in range(50)]