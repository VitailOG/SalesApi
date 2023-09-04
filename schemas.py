from datetime import date
from decimal import Decimal
from marshmallow import Schema, fields, validates, ValidationError, post_load, validates_schema


class InvoiceSchema(Schema):
    """ Additional obj income """
    customer_name = fields.String(required=True)
    invoice_number = fields.String(required=True)


class ItemSchema(Schema):
    """ Additional obj item """
    id = fields.Integer()
    title = fields.String(required=True)
    description = fields.String(required=True)
    price = fields.Decimal(places=2, rounding='ROUND_HALF_UP', as_string=True)
    item_type = fields.String(required=True)
    qty = fields.Integer(required=True)

    @validates("item_type")
    def validate_item_type(self, value):
        if value not in ('product', 'service'):
            raise ValidationError("Value should be 'product' or 'service'")


class CreateIncomeSchema(Schema):
    """ Common structure create income """
    invoice = fields.Nested(InvoiceSchema, many=False)
    item = fields.Nested(ItemSchema, many=False)

    @post_load(pass_many=True)
    def add_total_amount(self, data, many, **kwargs):
        item = data['item']
        data['total_amount'] = item['qty'] * Decimal(item['price'])
        return data


class ListInvoiceSchema(InvoiceSchema):
    """ For response list """
    id = fields.Integer(required=True)
    invoice_date = fields.DateTime(required=True)
    total_amount = fields.Decimal(places=2, rounding='ROUND_HALF_UP', as_string=True)
    children = fields.Nested(ItemSchema, many=False)


class UpdateIncomeSchema(InvoiceSchema):
    """ For update income """
    invoice_date = fields.Date(required=True)


class ExpenseSchema(InvoiceSchema):
    """ For expense """
    title = fields.String(required=True)
    qty = fields.Integer(required=True)
    invoice_date = fields.DateTime(required=True)


class ListExpenseSchema(InvoiceSchema):
    """ For expense """
    id = fields.Integer(required=True)
    qty = fields.Integer(required=True)
    total_amount = fields.Decimal(places=2, rounding='ROUND_HALF_UP', as_string=True)
    parent = fields.Nested(ItemSchema, many=False)


class ReportSchema(Schema):
    """ For report """
    start_date = fields.Date(allow_none=True, required=True)
    end_date = fields.Date(allow_none=True, required=True)

    @validates_schema
    def validate_data(self, data, **kwargs):
        if data['start_date'] is data['end_date'] is None:
            raise ValidationError("Set 'start_date' or 'end_date'")

    @post_load(pass_many=True)
    def add_total_amount(self, data, many, **kwargs):
        start_date, end_date = data['start_date'], data['end_date']
        match start_date, end_date:
            case date(), date():
                data["sql_condition"] = f"BETWEEN '{start_date}' AND '{end_date}'"
                data["filename"] = f"report_from_{start_date}_to_{end_date}"
            case date(), None:
                data["sql_condition"] = f"> '{start_date}'"
                data["filename"] = f"report_from_{start_date}"
            case None, date():
                data["sql_condition"] = f"< '{start_date}'"
                data["filename"] = f"report_to_{end_date}"
        return data


income_schema = CreateIncomeSchema()
list_income_schema = ListInvoiceSchema()
update_income_schema = UpdateIncomeSchema()

expense_schema = ExpenseSchema()
list_expense_schema = ListExpenseSchema()

report_schema = ReportSchema()

item_schema = ItemSchema()
