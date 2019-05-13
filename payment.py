from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
import time

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

class PaymentTypeDropDown(DropDown):
    data = ['Pay','Receive']
    def __init__(self, **kwargs):
        super(PaymentTypeDropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class PaymentModeDropDown(DropDown):
    data = ['Cash','Card','Credit']
    def __init__(self, **kwargs):
        super(PaymentModeDropDown, self).__init__(**kwargs)
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Button(text='%s' % self.data[index], size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class PaymentGrid(GridLayout):
    transaction_ref = ObjectProperty()
    card_four_digit = ObjectProperty()
    amount = ObjectProperty()
    payment_type = ObjectProperty()
    mode_of_payment = ObjectProperty()

class PaymentList(Screen):
    def on_pre_enter(self):
        self.pay.data = [{'transaction_ref': str('Transaction'+' '+str(x)),'card_four_digit':str('12'+str(x)),'amount':str(x),'payment_type':str('type'+str(x)),'mode_of_payment':str('mode'+str(x))}
                        for x in range(50)]
