from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.factory import Factory
from kivy.clock import Clock
import time, settings, datetime
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from pos_helper import pconn
from pony.orm import *


current_click_idx = ""
class Stock(Screen):
    item_code = ObjectProperty()
    item = ObjectProperty()
    sr_time = ObjectProperty()
    item_dp_widget = ObjectProperty()
    revised_stock = ObjectProperty()
    current_stock = ObjectProperty()
    stock_item = {}
    stock = []
    time = ObjectProperty(None)

    def __init__(self,**kwargs):
        super(Stock,self).__init__(**kwargs)
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.sr_time = str(self.time)
        Clock.schedule_interval(self.on_time,1/60.0)


    @db_session
    def on_pre_enter(self):  
        global current_click_idx
        if current_click_idx and current_click_idx != "":
            data = pconn.get_single_dbrecord(current_click_idx ,'StockReconciliation')
            if data:
                self.ids.sr_date.text = str(data.sr_date)
                self.ids.stock_reconciliation_items.data  = [{'idx': idx, 'record_id': e.id, 'instance':'StockReconciliationItem', 'pclass': self, 
                                    'item': (e.item.id,e.item_code),
                                    'item_code': e.item_code,'current_stock': e.current_stock if e.current_stock else 0.0,
                                    'revised_stock': e.revised_stock if e.revised_stock else 0.0} for idx, e in enumerate(data.stock_reconciliation_items)]          
                if self.item_dp_widget:
                    self.item_dp_widget.clear_widgets() 
        else:
            self.ids.sr_date.text = ""
            self.ids.stock_reconciliation_items.data  = []
            self.ids.sr_date.text = datetime.datetime.today().strftime('%d.%m.%Y')
    
 
    def cancel(self):
        self.ids.stock_reconciliation_items.data  = []
        global current_click_idx
        current_click_idx = ""

    def on_time(self,*args):
        self.time = time.strftime("%H:%M:%S", time.localtime())
        self.sr_time = str(self.time)

    def on_item_input(self):        
        if self.item_dp_widget:
            self.item_dp_widget.clear_widgets()    
        if self.ids.item_code.text != " " and self.ids.item_code.text != "":
            Factory.ItemCodeDropDown(self).open(self.ids.item_code)

    def save(self):
        #raise ValueError(self.ids.stock_reconciliation_items.data)
        self.stock = []
        stm = datetime.datetime.strptime(self.ids.sr_time.text,'%H:%M:%S')
        tm = stm.time()
        if self.ids.sr_date.text:
            dr = datetime.datetime.strptime(self.ids.sr_date.text, '%d.%m.%Y').strftime('%Y-%m-%d') 
            dt = datetime.datetime.strptime(dr,'%Y-%m-%d')
            dd = dt.date()
        for i in self.ids.stock_reconciliation_items.data:
            rev_stock = int(i["revised_stock"]) - int(i["current_stock"])
            if not rev_stock == 0:
                self.stock_item = {'idx': i["idx"],'record_id': 0,'instance':'StockLedger','pclass': self, 
                'sl_date':dd, 'sl_time': tm, 'item': i["item"], 'quantity': rev_stock}
                self.stock.append(self.stock_item)
                self.stock_item = {}    
        #raise ValueError(self.stock)
        payload = self
        res = pconn.insert_nested_dbrecord('StockReconciliation', payload, 
                    {'0':[],'StockReconciliationItem':["item_code"]}, 
                    {'0':['item_code'],'StockReconciliationItem':[]},
                    ["stock"]
                    )
        if res == "Success":
            self.manager.current= 'stock_list'
        else:
            pass

class StockGrid(GridLayout):
    sr_time = ObjectProperty()
    sr_date = ObjectProperty()
    idx = ObjectProperty()
    global current_click_idx
    current_click_idx = ""

    def line_click(self):
        global current_click_idx
        current_click_idx = self.idx
        self.parent.parent.parent.parent.parent.parent.manager.current= 'stock'
        self.parent.parent.parent.parent.parent.parent.manager.transition = SlideTransition(direction="right")

class StockList(Screen):
    def on_pre_enter(self):
        data = pconn.get_dbdata('StockReconciliation')   
        with db_session:
            if data:
                self.sto.data = [{'idx': str(x.id), 'sr_date': str(x.sr_date),'sr_time':str(x.sr_time)}
                            for x in data ]
            else:
                self.sto.data = []

    def make_current_click_idx_null(self):  
        global current_click_idx
        current_click_idx = ""

class StockReconciliationItemTable(RecycleDataViewBehavior, GridLayout):
    idx = None 
    item_code = ObjectProperty()
    current_stock = ObjectProperty()
    revised_stock = ObjectProperty()

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(StockReconciliationItemTable, self).refresh_view_attrs(
            rv, index, data)

    def remove_data(self):
        #self.parent.parent.data.pop(self.index)
        del self.parent.parent.data[self.index]

    def cal_stock(self, parent):
        parent.ids.stock_reconciliation_items.data[self.index].update({'revised_stock': float(self.ids.revised_stock.text if self.ids.revised_stock.text else 0 )})