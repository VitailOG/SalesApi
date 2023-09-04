from sqlalchemy import Enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class InvoiceBase(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    invoice_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    invoice_number = db.Column(db.String(255), nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    total_amount = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)


class IncomeInvoice(InvoiceBase):
    __tablename__ = "income_invoices"
    children = db.relationship('ProductAndService', backref='parent', cascade='all, delete-orphan', uselist=False)


class ExpenseInvoice(InvoiceBase):
    __tablename__ = "expense_invoices"
    qty = db.Column(db.Integer)
    product_and_service_id = db.Column(db.Integer, db.ForeignKey('products_and_services.id'), nullable=False)


class ProductAndService(db.Model):
    __tablename__ = "products_and_services"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    item_type = db.Column(Enum('product', 'service'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    income_invoice_id = db.Column(db.Integer, db.ForeignKey('income_invoices.id'), nullable=False)

    children = db.relationship('ExpenseInvoice', backref='parent', cascade='all, delete-orphan', uselist=False)
