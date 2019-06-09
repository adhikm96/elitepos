from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
import time

class Payment(Screen):
    p_date = ObjectProperty()
    p_time = ObjectProperty()
    transaction_ref = ObjectProperty()
    payment_type = ObjectProperty()
    mode_of_payment = ObjectProperty()
    card_four_digits = ObjectProperty()
    amount = ObjectProperty()

    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'Payment')
            if data:
                self.ids.transaction_ref.text = str(data.transaction_ref)
                self.ids.payment_type.text = str(data.payment_type)
                self.ids.mode_of_payment.text = str(data.mode_of_payment)
                self.ids.card_four_digits.text = str(data.card_four_digits)
                self.ids.amount.text = str(data.amount)
        else:
            self.ids.transaction_ref.text = ""
            self.ids.payment_type.text = "Select"
            self.ids.mode_of_payment.text = "Select"
            self.ids.card_four_digits.text = ""
            self.ids.amount.text = ""

    def cancel(self):
        self.ids.transaction_ref.text = ""
        self.ids.payment_type.text = "Select"
        self.ids.mode_of_payment.text = "Select"
        self.ids.card_four_digits.text = ""
        self.ids.amount.text = ""

    def save(self):
        global current_click_idx
        payload = self
        if current_click_idx and current_click_idx != "":
            res = pconn.update_single_dbrecord(current_click_idx, 'Tax', payload)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'tax_list'
            else:
                pass
        else:
            res = pconn.insert_single_dbrecord('Tax', payload)
            if res == "Success":
                self.manager.current= 'tax_list'
            else:
                pass

    time = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(Payment,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.p_time = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.p_time = str(self.time)

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
