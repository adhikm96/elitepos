from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.factory import Factory
from kivy.clock import Clock
import time, settings
from pos_helper import pconn
from pony.orm import *

current_click_idx = ""

class Payment(Screen):
    #p_date = ObjectProperty()
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
                self.ids.p_date.text = str(data.p_date)
        else:
            self.ids.transaction_ref.text = ""
            self.ids.payment_type.text = "Select"
            self.ids.mode_of_payment.text = "Select"
            self.ids.card_four_digits.text = ""
            self.ids.amount.text = ""
            self.ids.p_date.text = ""

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
            res = pconn.update_single_dbrecord(current_click_idx, 'Payment', payload)
            if res == "Success":
                current_click_idx = ""
                self.manager.current= 'payment_list'
            else:
                pass
        else:
            res = pconn.insert_single_dbrecord('Payment', payload)
            if res == "Success":
                self.manager.current= 'payment_list'
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
    imparent = ObjectProperty()
    def __init__(self,imparent, **kwargs):
        super(PaymentTypeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Factory.Custom_drop_down_button(text='%s' % self.data[index], text_size = self.imparent.ids.payment_type.size)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class PaymentModeDropDown(DropDown):
    data = ['Cash','Card','Credit']
    imparent = ObjectProperty()
    def __init__(self,imparent, **kwargs):
        super(PaymentModeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def add_buttons(self):
        for index in range(len(self.data)):
            btn = Factory.Custom_drop_down_button(text='%s' % self.data[index], text_size = self.imparent.ids.mode_of_payment.size)
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class SalePaymentTypeDropDown(DropDown):
    data = ['Pay','Receive']
    imparent = ObjectProperty()

    def __init__(self,imparent, **kwargs):
        super(SalePaymentTypeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def set_pay_type(self, cur):
        self.imparent.ids.payment_type.text = cur.text
        self.select(cur.text)

    def add_buttons(self):
        for index in self.data:
            btn = Factory.Custom_drop_down_button(text='%s' % index, text_size = self.imparent.ids.payment_type.size)
            btn.bind(on_release=self.set_pay_type)
            self.add_widget(btn)

class SalePaymentModeDropDown(DropDown):
    data = ['Cash','Card','Credit']
    imparent = ObjectProperty()

    def __init__(self,imparent, **kwargs):
        super(SalePaymentModeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def set_pay_mode(self, cur):
        self.imparent.ids.mode_of_payment.text = cur.text
        self.select(cur.text)

    def add_buttons(self):
        for index in self.data:
            btn = Factory.Custom_drop_down_button(text='%s' % index, text_size = self.imparent.ids.mode_of_payment.size)
            btn.bind(on_release=self.set_pay_mode)
            self.add_widget(btn)

class PurchasePaymentTypeDropDown(DropDown):
    data = ['Pay','Receive']
    imparent = ObjectProperty()

    def __init__(self,imparent, **kwargs):
        super(PurchasePaymentTypeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def set_pay_type(self, cur):
        self.imparent.ids.payment_type.text = cur.text
        self.select(cur.text)

    def add_buttons(self):
        for index in self.data:
            btn = Factory.Custom_drop_down_button(text='%s' % index, text_size = self.imparent.ids.payment_type.size)
            btn.bind(on_release=self.set_pay_type)
            self.add_widget(btn)

class PurchasePaymentModeDropDown(DropDown):
    data = ['Cash','Card','Credit']
    imparent = ObjectProperty()

    def __init__(self,imparent, **kwargs):
        super(PurchasePaymentModeDropDown, self).__init__(**kwargs)
        self.imparent = imparent
        self.add_buttons()

    def set_pay_mode(self, cur):
        self.imparent.ids.mode_of_payment.text = cur.text
        self.select(cur.text)

    def add_buttons(self):
        for index in self.data:
            btn = Factory.Custom_drop_down_button(text='%s' % index, text_size = self.imparent.ids.mode_of_payment.size)
            btn.bind(on_release=self.set_pay_mode)
            self.add_widget(btn)

class PaymentGrid(GridLayout):
    idx = ObjectProperty()
    global current_click_idx
    current_click_idx = ""
    p_date = ObjectProperty()
    p_time = ObjectProperty()
    transaction_ref = ObjectProperty()
    payment_type = ObjectProperty()
    mode_of_payment = ObjectProperty()
    card_four_digits = ObjectProperty()
    amount = ObjectProperty()
    imparent = ObjectProperty()

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'payment'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")

class PaymentList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('Payment')   
        with db_session:
            self.pay.data = [{'idx': str(x.id), 'p_date': str(x.p_date),'p_time':str(x.p_time),'transaction_ref':str(x.transaction_ref),'payment_type':str(x.payment_type),'mode_of_payment':str(x.mode_of_payment),'card_four_digits':str(x.card_four_digits),'amount':str(x.amount)}
                            for x in data]

    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""