from datetime import date
from datetime import time
from pony.orm import *

db = Database()

class User(db.Entity):
    _table_ = 'Users'
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    email_address = Optional(str)
    password = Optional(str)
    
class Customer(db.Entity):
    _table_ = 'Customers'
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    email_address = Optional(str)
    contact_number = Optional(int)
    address = Optional(str)
    sales_invoices = Set('SalesInvoice')


class SalesInvoice(db.Entity):
    _table_ = 'SalesInvoices'
    id = PrimaryKey(int, auto=True)
    customer = Required(Customer)
    invoice_date = Optional(date)
    invoice_time = Optional(time)
    sales_invoice_items = Set('SalesInvoiceItem')
    subtotal = Optional(float)
    discount = Optional(float)
    taxes = Optional(float)
    total = Optional(float)
    payments = Set('Payment')


class Item(db.Entity):
    _table_ = 'Items'
    id = Required(int)
    item_code = Required(str)
    name = Optional(str)
    category = Optional(str)
    valuation_rate = Optional(float)
    sales_invoice_items = Set('SalesInvoiceItem')
    purchase_invoice_items = Set('PurchaseInvoiceItem')
    stock_reconciliation_items = Set('StockReconciliationItem')
    stock_ledgers = Set('StockLedger')
    tax_items = Set('TaxItem')
    PrimaryKey(id, item_code)


class Supplier(db.Entity):
    _table_ = 'Suppliers'
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    address = Optional(str)
    tax_no = Optional(str)
    contact_number = Optional(str)
    email_address = Optional(str)
    purchaseinvoices = Set('PurchaseInvoice')


class Tax(db.Entity):
    _table_ = 'Taxes'
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    tax_type = Optional(str)
    percent = Optional(float)
    tax_items = Set('TaxItem')


class SalesInvoiceItem(db.Entity):
    _table_ = 'SalesInvoiceItems'
    id = PrimaryKey(int, auto=True)
    sales_invoice = Required(SalesInvoice)
    item_code = Optional(str)
    rate = Optional(float)
    quantity = Optional(int)
    discount = Optional(float)
    discount_percent = Optional(float)
    amount = Optional(float)
    tax_string = Optional(str)
    item = Required(Item)


class PurchaseInvoice(db.Entity):
    _table_ = 'PurchaseInvoices'
    id = PrimaryKey(int, auto=True)
    invoice_date = Optional(date)
    invoice_time = Optional(time)
    supplier = Required(Supplier)
    subtotal = Optional(float)
    discount = Optional(float)
    taxes = Optional(float)
    total = Optional(float)
    delivery_date = Optional(date)
    delivery_time = Optional(time)
    notes = Optional(str)
    purchase_invoice_items = Set('PurchaseInvoiceItem')
    payments = Set('Payment')


class PurchaseInvoiceItem(db.Entity):
    _table_ = 'PurchaseInvoiceItems'
    id = PrimaryKey(int, auto=True)
    purchase_invoice = Required(PurchaseInvoice)
    item_code = Optional(str)
    rate = Optional(float)
    quantity = Optional(int)
    discount = Optional(float)
    discount_percent = Optional(float)
    amount = Optional(float)
    tax_string = Optional(str)
    item = Required(Item)


class StockReconciliation(db.Entity):
    _table_ = 'StockReconciliations'
    id = PrimaryKey(int, auto=True)
    sr_date = Optional(date)
    sr_time = Optional(time)
    stock_reconciliation_items = Set('StockReconciliationItem')


class StockReconciliationItem(db.Entity):
    _table_ = 'StockReconciliationItems'
    id = PrimaryKey(int, auto=True)
    item_code = Optional(str)
    current_stock = Optional(float)
    revised_stock = Optional(float)
    stock_reconciliation = Required(StockReconciliation)
    item = Required(Item)


class Payment(db.Entity):
    _table_ = 'Payments'
    id = PrimaryKey(int, auto=True)
    p_date = Optional(date)
    p_time = Optional(time)
    transaction_doc = Optional(str)
    transaction_ref = Optional(str)
    payment_type = Optional(str)
    mode_of_payment = Optional(str)
    card_four_digits = Optional(int)
    amount = Optional(float)
    sales_invoice = Optional(SalesInvoice)
    purchase_invoice = Optional(PurchaseInvoice)


class PaymentLedger(db.Entity):
    _table_ = 'PaymentLedgers'
    id = PrimaryKey(int, auto=True)
    account = Optional('Account')
    debit = Optional(float)
    credit = Optional(float)
    amount = Optional(float)
    transaction_doc = Optional(str)
    transaction_ref = Optional(str)
    pl_date = Optional(date)
    pl_time = Optional(time)


class StockLedger(db.Entity):
    _table_ = 'StockLegers'
    id = PrimaryKey(int, auto=True)
    item = Required(Item)
    quantity = Optional(int)
    transaction_doc = Optional(str)
    transaction_ref = Optional(str)
    sl_date = Optional(date)
    sl_time = Optional(time)



class TaxItem(db.Entity):
    id = PrimaryKey(int, auto=True)
    percent = Optional(float)
    amount = Optional(float)
    tax = Required(Tax)
    item = Required(Item)
    
class Category(db.Entity):
    _table_ = 'Category'
    id = PrimaryKey(int, auto=True)
    name = Optional(str)

class Account(db.Entity):
    _table_ = 'Accounts'
    id = PrimaryKey(int, auto=True)
    account_name = Optional(str)
    account_type = Optional(str)
    activity = Optional(str)
    payment_ledgers = Set('PaymentLedger')


# db.generate_mapping()
# db.generate_mapping(create_tables=True)