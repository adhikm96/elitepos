from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
import time, settings, datetime
from pos_helper import pconn
import json
from kivy.factory import Factory
from pony.orm import *
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.recycleview.views import RecycleDataViewBehavior


class PurchasePaymentPopup(Popup):
    p_date = ObjectProperty()
    p_time = ObjectProperty()
    transaction_ref = ObjectProperty()
    payment_type = ObjectProperty()
    mode_of_payment = ObjectProperty()
    card_four_digits = NumericProperty()
    amount = NumericProperty()
    imparent = ObjectProperty()
    purchase_invoice_items = []
    payments = []

    payments = {}


    def save(self): 
        if float(self.imparent.ids.total.text) < float(self.ids.amount.text):
            Factory.warning_pop("Payment amount is greater than billing total").open()
        else:
            self.payments = {}
            for i in self.ids:
                if hasattr(self.ids[i], 'text'):
                    if i == "card_four_digits":
                        self.payments[i] = int(self.ids[i].text) if self.ids[i].text else ""
                    elif i == "amount":
                        self.payments[i] = float(self.ids[i].text) if self.ids[i].text else ""
                    elif i == "p_date":
                        dr = datetime.datetime.strptime(self.ids[i].text, '%d.%m.%Y').strftime('%Y-%m-%d') 
                        dt = datetime.datetime.strptime(dr,'%Y-%m-%d')
                        dd = dt.date()
                        self.payments[i] = dd
                    elif i == "p_time":
                        dt = datetime.datetime.strptime(self.ids[i].text,'%H:%M:%S')
                        dd = dt.time()
                        self.payments[i] = dd
                    else:
                        self.payments[i] = self.ids[i].text or ""
            self.payments.update({'idx': len(self.imparent.ids.payments.data),'record_id': 0,'instance':'Payment','pclass': self.imparent}) 
            
            self.imparent.ids.payments.data.append(self.payments)
            self.dismiss()
            
            #raise ValueError(self.imparent.ids.payments.data)
            if float(self.imparent.ids.total.text) == float(self.ids.amount.text):
                self.imparent.save()

    def __init__(self, imparent,**kwargs):
        super(PurchasePaymentPopup,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.p_time = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)
        self.imparent = imparent
        self.ids.amount.text = imparent.ids.total.text

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.p_time = str(self.time)

current_click_idx = ""

class PurchaseItemPopup(Popup):
    imparent = ObjectProperty()
    item_code = ObjectProperty()
    name = ObjectProperty()
    category = ObjectProperty()
    valuation_rate = ObjectProperty()

    def __init__(self, imparent,**kwargs):
        super(PurchaseItemPopup,self).__init__(**kwargs)
        self.imparent = imparent
        self.ids.item_code.text = imparent.ids.item_code.text

    def save(self):
        payload = self
        res = pconn.insert_nested_dbrecord('Item', payload, {'0':[]}, {'0':[]})
        if res == "Success":
            rec = pconn.query_search('Item', self.ids.item_code.text)
            with db_session:
                if rec:
                    for index, e in enumerate(rec):
                        self.imparent.ids.purchase_invoice_items.data.append({'idx':  len(self.imparent.ids.purchase_invoice_items.data),'record_id': 0,
                                      'instance':'PurchaseInvoiceItem','pclass': self,'item': (e.id,e.item_code),
                                      'item_code': e.item_code,'rate': str(e.valuation_rate if e.valuation_rate else 0.0),'quantity': "1" ,
                                      'discount': 0 , 'discount_percent': 0})
                        self.imparent.ids.item_code.text = ""
                        self.dismiss()
                    

class Purchase(Screen):
    invoice_time = ObjectProperty()
    invoice_date = ObjectProperty()
    item_code = StringProperty()
    subtotal = ObjectProperty()
    supplier = ObjectProperty()
    supplier_name = ObjectProperty()
    discount = ObjectProperty()
    discount_percent = ObjectProperty()
    taxes = ObjectProperty()
    tax_list = []
    total = ObjectProperty()
    notes = ObjectProperty()
    item_dp_widget = ObjectProperty()
    supplier_dp_widget = ObjectProperty()
    supplier_selected = StringProperty()
    stock_item = {}
    stock = []
    journal_entry = []

    @db_session
    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'PurchaseInvoice')
            if data:
                self.ids.supplier_name.text = str(data.supplier.name)
                self.supplier = data.supplier.id
                self.ids.subtotal.text = str(data.subtotal)
                self.ids.discount.text = str(data.discount)
                self.ids.taxes.text = str(data.taxes)
                self.ids.total.text = str(data.total)
                self.ids.notes.text = str(data.notes)
                self.ids.invoice_date.text = str(data.invoice_date)
                self.ids.purchase_invoice_items.data  = [{'idx': idx, 'record_id': e.id, 'instance':'PurchasesInvoiceItem', 'pclass': self, 
                                    'item': (e.item.id,e.item_code),
                                    'item_code': e.item_code, 'rate': float(e.rate), 'discount': float(e.discount) if e.discount else 0.0, 
                                    'discount_percent': float(e.discount_percent) if e.discount_percent else 0.0, 'tax_string': e.tax_string 
                                    if e.tax_string else "", 'amount': float(e.amount)if e.amount else 0.0 } for idx, e in enumerate(data.purchase_invoice_items)]       
                self.ids.payments.data  = [{'idx': idx, 'record_id': e.id, 'instance':'Payment', 'pclass': self,'transaction_ref':e.transaction_ref if e.transaction_ref else "",
                                    'payment_type': e.payment_type if e.payment_type else "",'mode_of_payment':e.mode_of_payment if e.mode_of_payment else "",
                                    'card_four_digits':int(e.card_four_digits) if e.card_four_digits else "",'amount':float(e.amount)if e.amount else 0.0,
                                    'p_date': e.p_date if e.p_date else "",'p_time': e.p_time if e.p_time else ""
                                    } for idx, e in enumerate(data.payments)]
                if self.supplier_dp_widget:
                    self.supplier_dp_widget.clear_widgets()   
    
                self.tax_list = []
                for index, i in enumerate(self.ids.purchase_invoice_items.data):
                    if "tax_string" in i:
                        tax_dic = json.loads(i["tax_string"])
                        self.recalculate_taxes( tax_dic,index, i["item_code"], i["amount"])
        else:
            self.ids.supplier_name.text = ""
            self.supplier = ""
            self.ids.subtotal.text = "0.0"
            self.ids.discount.text = "0"
            self.ids.taxes.text = "0"
            self.ids.total.text = "0.0"
            self.ids.notes.text = ""
            self.ids.purchase_invoice_items.data  = []
            self.ids.payments.data = []
            self.ids.invoice_date.text = datetime.datetime.today().strftime('%d.%m.%Y')
            self.tax_list = []
 
    def cancel(self):
        self.ids.supplier_name.text = ""
        self.ids.subtotal.text = ""
        self.ids.discount.text = ""
        self.ids.taxes.text = ""
        self.ids.total.text = ""
        self.ids.notes.text = ""
        self.ids.purchase_invoice_items.data  = []
        self.ids.payments.data = []
        global current_click_idx
        current_click_idx = ""


    def save(self):
        dr = datetime.datetime.strptime(self.ids.invoice_date.text, '%d.%m.%Y').strftime('%Y-%m-%d') 
        dt = datetime.datetime.strptime(dr,'%Y-%m-%d')
        dd = dt.date()
        stm = datetime.datetime.strptime(self.ids.invoice_time.text,'%H:%M:%S')
        tm = stm.time()

        self.journal_entry = []
        sale_entry = pconn.get_single_dbrecord_wpk("Account", "activity", "Inventory")
        with db_session:
            for i in sale_entry:
                self.journal_entry.append({'account': i.id,'debit': float(self.ids.subtotal.text),'idx': len(self.journal_entry),
                            'record_id': 0,'instance':'PaymentLedger','pclass': self,'pl_date': dd,'pl_time': tm})


            tax_entry = pconn.get_single_dbrecord_wpk("Account", "activity", "Tax")
            for i in tax_entry:
                self.journal_entry.append({'account':i.id,'debit': float(self.ids.taxes.text),'idx': len(self.journal_entry),
                            'record_id': 0,'instance':'PaymentLedger','pclass': self,'pl_date': dd,'pl_time': tm})

            for j in self.ids.payments.data:
                if j["mode_of_payment"] == "Cash":
                    cash_entry = pconn.get_single_dbrecord_wpk("Account", "activity", "Cash")
                    for i in cash_entry:
                        self.journal_entry.append({'account':i.id,'credit': float(j["amount"]),'idx': len(self.journal_entry),
                            'record_id': 0,'instance':'PaymentLedger','pclass': self,'pl_date': dd,'pl_time': tm})

                elif j["mode_of_payment"] == "Card":
                    bank_entry = pconn.get_single_dbrecord_wpk("Account", "activity", "Bank")
                    for i in bank_entry:
                        self.journal_entry.append({'account': i.id,'credit': float(j["amount"]),'idx': len(self.journal_entry),
                            'record_id': 0,'instance':'PaymentLedger','pclass': self,'pl_date': dd,'pl_time': tm})

                elif j["mode_of_payment"] == "Credit":
                    credit_entry = pconn.get_single_dbrecord_wpk("Account", "activity", "Supplier-Credit")
                    for i in credit_entry:
                        self.self.journal_entry.append({'account': i.id,'credit': float(j["amount"]),'idx': len(self.journal_entry),
                            'record_id': 0,'instance':'PaymentLedger','pclass': self,'pl_date': dd,'pl_time': tm})
        #raise ValueError(self.tax_list)
        self.stock = []
        for index, i in enumerate(self.ids.purchase_invoice_items.data):
            for f in i:
                if f == "item":
                    self.stock_item[f] = i[f]
                elif f == "quantity":
                    self.stock_item[f] = i[f]
            self.stock_item.update({'idx': index,'record_id': 0,'instance':'StockLedger','pclass': self,'sl_date': dd,'sl_time': tm})
            self.stock.append(self.stock_item)
            self.stock_item = {}
        if not self.ids.supplier_name.text:
            Factory.warning_pop("Please select Supplier").open()
        elif self.ids.purchase_invoice_items.data  == []:
            Factory.warning_pop("Please select Items").open()
        elif self.ids.payments.data  == []:
            Factory.warning_pop("Please do payment").open()
        else:
            self.ids.supplier = self.ids.supplier_name
            self.ids.supplier.text = str(self.supplier)
            global current_click_idx
            payload = self
            if current_click_idx and current_click_idx != "":
                res = pconn.update_nested_dbrecord(current_click_idx, 'PurchaseInvoice', payload, {'0':[],"PurchaseInvoiceItem":["item"],"Payment":['amount']}, {'0':["supplier_name"],"PurchaseInvoiceItem":[],"Payment":[]})
                if res == "Success":
                    current_click_idx = ""
                    self.manager.current= 'purchase_list'
                else:
                    pass
            else:
                res = pconn.insert_nested_dbrecord('PurchaseInvoice', payload, {'0':[],"PurchaseInvoiceItem":["item"],"Payment":['amount']}, {'0':["supplier_name","item_code"],
                    "PurchaseInvoiceItem":[],"Payment":[]},["stock","journal_entry"])
                if res == "Success":
                    self.manager.current= 'purchase_list'
                else:
                    pass

    time = ObjectProperty(None)
    def __init__(self,**kwargs):
        super(Purchase,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.invoice_time = str(self.time)
        #self.invoice_date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        Clock.schedule_interval(self.on_time,1/60.0)

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.invoice_time = str(self.time)

    def on_supplier_input(self):
        if self.supplier_dp_widget:
            self.supplier_dp_widget.clear_widgets()    
        if self.ids.supplier_name.text != " " and self.ids.supplier_name.text != "" and self.supplier_selected != self.ids.supplier_name.text:
            Factory.SupplierDropDown(self).open(self.ids.supplier_name)

    def on_item_input(self):        
        if self.item_dp_widget:
            self.item_dp_widget.clear_widgets()    
        if self.ids.item_code.text != " " and self.ids.item_code.text != "":
            Factory.PurchaseItemCodeDropDown(self).open(self.ids.item_code)

    @db_session
    def on_focus(instance, value):
        other_focussed_flag = False
        for e in instance.ids:
            if e != "customer_name" and getattr(instance.ids[e], "focus", False):
                other_focussed_flag = True

        if not instance.ids.supplier_name.focus and other_focussed_flag:
            rec = pconn.get_single_dbrecord_wpk("Supplier", "name", value)
            if len(rec) <= 0:
                instance.ids.supplier_name.text = ""
                instance.ids.supplier = ""
                instance.supplier_selected = ""

    def cal_tot(self):
        self.ids.total.text = str(float(self.ids.subtotal.text if self.ids.subtotal.text else 0.0 ) - float(self.ids.discount.text if self.ids.discount.text else 0.0)
                               + float(self.ids.taxes.text if self.ids.taxes.text else 0.0 ))
    

    def open_item_pop(self):
        rec = pconn.query_search('Item', self.ids.item_code.text)
        with db_session:
            if rec:
                for index, e in enumerate(rec):
                    self.ids.purchase_invoice_items.data.append({'idx':  len(self.ids.purchase_invoice_items.data),'record_id': 0,
                                              'instance':'PurchaseInvoiceItem','pclass': self,'item': (e.id,e.item_code),
                                              'item_code': e.item_code,'rate': str(e.valuation_rate if e.valuation_rate else 0.0),'quantity': "1" ,
                                              'discount': 0 , 'discount_percent': 0})
                    self.ids.item_code.text = ""
            else:
                Factory.PurchaseItemPopup(self).open()

    def recalculate_taxes(self, tax_info, idx=None, item_code=None, amount=None):
        # print("...........{0}".format(idx))
        # print(tax_info, item_code, amount)
        tax_amount = 0
        tax_rate = 0
        if tax_info:
            self.tax_list.append(tax_info)
        if idx >= 0 and item_code and amount:
            for e in self.tax_list[idx][item_code]:
                if e['amount'] > 0:
                    tax_amount = amount + float(e['amount'])
                elif e['percent'] > 0:
                    tax_amount = amount * float(e['percent'])/100
                e['tax_applied'] = tax_amount
                e['taxable_amount'] = amount
        
        total_tax = 0
        total_taxable_amount = 0        
        for e in self.tax_list:
            for f in e:
                temp_tx = 0
                for g in e[f]:
                    total_tax += float(g['tax_applied'] if g.has_key('tax_applied') else 0.00)
                    temp_tx = float(g['taxable_amount'] if g.has_key('taxable_amount') else 0.00)
                total_taxable_amount += temp_tx
        print(total_tax, total_taxable_amount)
        self.ids.taxes.text = str(total_tax)
        self.ids.total.text = str(total_tax + total_taxable_amount)
        self.ids.subtotal.text = str(total_taxable_amount)

class PurchaseTable(RecycleDataViewBehavior, GridLayout):
    item = ObjectProperty()
    item_code = ObjectProperty()
    rate = NumericProperty()

    discount = NumericProperty()
    discount_percent = NumericProperty()
    amount = NumericProperty()
    idx = None 
    quantity = ObjectProperty()
    index = ObjectProperty()

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.idx = data['idx']
        self.pclass = data['pclass']
        self.item = data['item']
        self.index = index
        return super(PurchaseTable, self).refresh_view_attrs(
            rv, index, data)

    def remove_data(self, p):
        tot = 0
        #self.parent.parent.data.pop(self.index)
        del self.parent.parent.data[self.index]
        del p.tax_list[self.index]
        p.recalculate_taxes({})
        for i in p.ids.purchase_invoice_items.data:
            if "amount" in i:
                tot = tot + float(i["amount"])
        p.ids.subtotal.text = str(tot)

    def cal_amt(self,p):
        #raise ValueError(self.ids.rate.text if not  self.ids.rate.text == "" else 0.0)
        amt = float(self.ids.rate.text if not  self.ids.rate.text == "" else 0.0) * int(self.ids.quantity.text if not  self.ids.quantity.text == "" else 0)
        disc_per = (float(amt if not  amt == "" else 0.0) * float(self.ids.discount_percent.text if not  self.ids.discount_percent.text == "" else 0.0))/ 100
        net_amt = amt - float(disc_per) - float(self.ids.discount.text if not  self.ids.discount.text == "" else 0.0)
        
        self.ids.amount.text = str(net_amt)

        p.ids.purchase_invoice_items.data[self.index].update({'rate': float(self.ids.rate.text) if self.ids.rate.text else 0.0,
                                'discount_percent': float(self.ids.discount_percent.text) if self.ids.discount_percent.text else 0.0,
                                'discount': float(self.ids.discount.text) if self.ids.discount.text else 0.0,
                                'amount': float(self.ids.amount.text) if self.ids.amount.text else 0.0,'quantity': int(self.ids.quantity.text)})
        p.ids.subtotal.text = ""
        sub_tot = 0.0
        for i in p.ids.purchase_invoice_items.data:
            if "amount" in i:
                sub_tot  = sub_tot + float(i["amount"])
        p.ids.subtotal.text = str(sub_tot)
        p.ids.total.text = str(sub_tot)
        p.recalculate_taxes({}, self.index, self.ids.item_code.text, net_amt)

class PurchaseGrid(GridLayout):
    idx = ObjectProperty()
    invoice_time = ObjectProperty()
    invoice_date = ObjectProperty()
    subtotal = ObjectProperty()
    supplier = ObjectProperty()
    discount = ObjectProperty()
    taxes = ObjectProperty()
    total = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'purchase'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")
    

class PurchaseList(Screen):
    supplier_dp_widget = ObjectProperty()
    supplier_selected = StringProperty()
    def on_pre_enter(self):
        self.ids.selected_supplier.text = ""
        self.ids.selected_date.text = ""
        data = pconn.get_dbdata('PurchaseInvoice')   
        with db_session:
            if data:
                self.purlist.data = [{'idx': str(x.id), 'supplier': str(x.supplier.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                            for x in data ]
            else:
                self.purlist.data = []

    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""

    def on_search_date(self):
        self.laDate = self.ids.selected_date.text
        if self.laDate:
            self.datepicked = datetime.datetime.strptime(self.laDate, '%d.%m.%Y').strftime('%Y-%m-%d') 
            dategive = datetime.datetime.strptime(self.datepicked, '%Y-%m-%d').date()
            if not self.ids.selected_supplier.text:
                data = pconn.get_single_dbrecord_wpk("PurchaseInvoice", "invoice_date", dategive)
                with db_session:
                    if data:
                        self.purlist.data = [{'idx': str(x.id), 'supplier': str(x.supplier.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                            for x in data ]
                    else:
                        self.purlist.data = []
            else: 
                data = pconn.get_search_dbrecord_wpk_by_name_date("PurchaseInvoice","supplier",self.ids.selected_supplier.text, "invoice_date", dategive)
                with db_session:
                    if data:
                        self.purlist.data = [{'idx': str(x.id), 'supplier': str(x.supplier.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                            for x in data ]
                    else:
                        self.purlist.data = []

    def on_supplier_input_for_search(self):
        if self.ids.selected_supplier.text and not self.ids.selected_date.text:
            if self.supplier_dp_widget:
                self.supplier_dp_widget.clear_widgets()    
            if self.ids.selected_supplier.text != " " and self.ids.selected_supplier.text != "" and self.supplier_selected != self.ids.selected_supplier.text:
                Factory.SearchSupplierDropDown(self).open(self.ids.selected_supplier)

        elif not self.ids.selected_supplier.text and self.ids.selected_date.text:
            self.laDate = self.ids.selected_date.text
            self.datepicked = datetime.datetime.strptime(self.laDate, '%d.%m.%Y').strftime('%Y-%m-%d') 
            dategive = datetime.datetime.strptime(self.datepicked, '%Y-%m-%d').date()
            data = pconn.get_single_dbrecord_wpk("PurchaseInvoice", "invoice_date", dategive)
            with db_session:
                if data:
                    self.purlist.data = [{'idx': str(x.id), 'supplier': str(x.supplier.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                            for x in data ]
                else:
                    self.purlist.data = []

        elif self.ids.selected_supplier.text and self.ids.selected_date.text:
            if self.supplier_dp_widget:
                self.supplier_dp_widget.clear_widgets()    
            if self.ids.selected_supplier.text != " " and self.ids.selected_supplier.text != "" and self.supplier_selected != self.ids.selected_supplier.text:
                Factory.SearchSupplierDropDown(self).open(self.ids.selected_supplier)

        else:
            data = pconn.get_dbdata('PurchaseInvoice')   
            with db_session:
                if data:
                    self.purlist.data = [{'idx': str(x.id), 'supplier': str(x.supplier.name),'subtotal':str(x.subtotal),'discount':str(x.discount),'taxes':str(x.taxes), 'total':str(x.total),'invoice_date':str(x.invoice_date)}
                            for x in data ]
                else:
                    self.purlist.data = []

class PurchasePaymentTable(RecycleDataViewBehavior, GridLayout):
    p_date = ObjectProperty()
    p_time = ObjectProperty()
    transaction_ref = ObjectProperty()
    payment_type = ObjectProperty()
    mode_of_payment = ObjectProperty()
    card_four_digits = ObjectProperty()
    amount = ObjectProperty()