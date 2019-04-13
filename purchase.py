from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
import time

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

