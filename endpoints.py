from flask import request, send_file
from flask_restful import Resource
from sqlalchemy.orm.exc import NoResultFound

from service import ReportGenerator
from schemas import (
    income_schema, expense_schema, report_schema, update_income_schema,
    item_schema, list_income_schema, list_expense_schema
)
from repositories import IncomeRepo, ProductAndServiceRepo, ExpenseRepo


class BaseResource(Resource):
    repository = None
    schemas: dict[str, object] = None

    @property
    def get_schema(self):
        return self.schemas[request.method.lower()]

    def delete(self, pk):
        try:
            self.repository.delete(pk)
        except NoResultFound:
            return {"success": False}
        return {"success": True}

    def put(self, pk):
        self.repository.update(
            pk, self.get_schema.load(request.get_json())
        )
        return {"success": True}


class IncomeResource(BaseResource):
    repository = IncomeRepo
    schemas = {
        "put": update_income_schema,
        "post": income_schema
    }

    def post(self):
        """
        {
            "invoice": {
                "customer_name": "ФОП Петренко",
                "invoice_number": "332143"
            },
            "item": {
                "title": "Туалетна бумага",
                "description": "Туалетна бумага",
                "price": "100.50",
                "item_type": "product",
                "qty": 10
            }
        }
        """
        self.repository.create(
            income_schema.load(request.get_json())
        )
        return {"success": True}

    def get(self):
        return list_income_schema.dump(IncomeRepo.all(), many=True)


class ExpenseResource(BaseResource):
    repository = ExpenseRepo

    def post(self):
        """
        {
            "title": "Туалетна бумага",
            "qty": 5,
            "invoice_number": "das",
            "customer_name": "asd"
        }
        """
        return ExpenseRepo.create(
            expense_schema.load(request.get_json())
        )

    def put(self, pk):
        """
        {
            "title": "Камаз",
            "qty": 2,
            "invoice_number": "111111111",
            "customer_name": "asd"
        }
        """
        return ExpenseRepo.update(
            pk, expense_schema.load(request.get_json())
        )

    def get(self):
        return list_expense_schema.dump(ExpenseRepo.all(), many=True)


class ItemResource(Resource):

    def put(self, pk):
        """
        {
            "title": "Туалетна бумага",
            "description": "Туалетна бумага",
            "price": "100.50",
            "item_type": "product",
            "qty": 10
        }
        """
        ProductAndServiceRepo.update(
            pk, item_schema.load(request.get_json()), with_commit=True
        )
        return {"Updated": True}


class ReportResource(Resource):

    def post(self):
        """
        {
            "start_date": "2023-09-01",
            "end_date": "2023-09-04"
        }
        """
        validated_data = report_schema.load(request.get_json())
        return send_file(
            ReportGenerator(validated_data['sql_condition'])(),
            as_attachment=True,
            download_name=f"{validated_data['filename']}.pdf",
            mimetype='application/pdf'
        )
