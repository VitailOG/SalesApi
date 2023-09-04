from sqlalchemy import update
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.exc import NoResultFound

from config import ERROR_MESSAGE_PATTERN
from models import IncomeInvoice, ProductAndService, ExpenseInvoice, db


class CRUDBase:
    model = None

    @classmethod
    def delete(cls, pk: int):
        obj = cls.model.query.get(pk)

        if obj is None:
            raise NoResultFound

        db.session.delete(obj)
        db.session.commit()

    @classmethod
    def update(cls, pk: int, data: dict):
        db.session.execute(
            update(cls.model)
            .where(cls.model.id == pk)
            .values(**data)
        )
        db.session.commit()


class ProductAndServiceRepo:
    model = ProductAndService

    @classmethod
    def get_by_title(cls, name: str):
        stmt = (
            db.session
            .query(
                db.func.sum(ExpenseInvoice.qty).label("sum"),
                ExpenseInvoice.product_and_service_id
            )
            .select_from(ExpenseInvoice)
            .subquery()
        )

        product = (
            db.session
            .query(
                ProductAndService.id,
                ProductAndService.price,
                db.func.coalesce(ProductAndService.qty - stmt.c.sum, ProductAndService.qty)
            )
            .filter(ProductAndService.title == name)
            .filter(ProductAndService.is_available.is_(True))
            .join(IncomeInvoice, IncomeInvoice.id == ProductAndService.income_invoice_id)
            .outerjoin(stmt, ProductAndService.id == stmt.c.product_and_service_id)
            .order_by(IncomeInvoice.invoice_date.asc())
            .first()
        )

        if product is None:
            raise NoResultFound

        return product

    @classmethod
    def create(cls, data: dict):
        db.session.add(ProductAndService(**data))

    @classmethod
    def update(cls, pk: int, data: dict, *, with_commit: bool = False):
        item = cls.model.query.get(pk)

        for field, value in data.items():
            setattr(item, field, value)

        if any(_ in data for _ in ("price", "qty")):
            income = IncomeInvoice.query.get(item.income_invoice_id)
            price = data.get("price", item.price)
            qty = data.get("qty", item.qty)
            income.total_amount = price * qty

        if with_commit:
            db.session.commit()


class IncomeRepo(CRUDBase):
    model = IncomeInvoice

    @classmethod
    def create(cls, data: dict):
        income = cls.model(**data['invoice'] | {"total_amount": data['total_amount']})
        db.session.add(income)
        db.session.flush()
        ProductAndServiceRepo.create(data['item'] | {"income_invoice_id": income.id})
        db.session.commit()

    @classmethod
    def all(cls):
        return cls.model.query.options(selectinload(cls.model.children)).all()


class ExpenseRepo(CRUDBase):
    model = ExpenseInvoice

    @classmethod
    def get(cls):
        return """
            select
                ps.id 'Ідентифікатор',
                ps.title 'Назва',
                ps.price 'Ціна за одиницю',
                ps.price * sum(e.qty) 'Сума',
                ps.qty 'Кількість на складі',
                ps.qty - sum(e.qty) 'Залишок на складі'
            from expense_invoices e
            join products_and_services ps on ps.id = e.product_and_service_id
            where invoice_date %s
            group by 1,2,3;
        """

    @classmethod
    def create(cls, data):
        with db.session.begin():
            product_id, price, qty, *_ = ProductAndServiceRepo.get_by_title(data.pop('title'))

            qty_difference = qty - data['qty']

            if qty_difference < 0:
                return {"success": False, "message": ERROR_MESSAGE_PATTERN % (qty, data['qty'])}

            elif qty_difference == 0:
                ProductAndServiceRepo.update(product_id, {"is_available": False})

            data = data | {"product_and_service_id": product_id, "total_amount": price * data['qty']}

            db.session.add(ExpenseInvoice(**data))

            db.session.commit()
            return {"success": True, "message": "Created"}

    @classmethod
    def update(cls, pk, data):
        product_id, price, qty, *_ = ProductAndServiceRepo.get_by_title(data.pop('title'))

        expense = cls.model.query.get(pk)

        qty_difference = qty + expense.qty - data['qty']

        if qty_difference < 0:
            return {"success": False, "message": ERROR_MESSAGE_PATTERN % (qty, data['qty'])}

        elif qty_difference == 0:
            ProductAndServiceRepo.update(product_id, {"is_available": False})

        for field, value in data.items():
            setattr(expense, field, value)

        db.session.commit()
        return {"success": True, "message": "Created"}

    @classmethod
    def all(cls):
        return cls.model.query.all()
