from flask import Flask
from flask_restful import Api
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import NoResultFound

from models import db
from endpoints import IncomeResource, ExpenseResource, ReportResource, ItemResource


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)
ma = Marshmallow(app)


# @app.errorhandler(NoResultFound)
# def handle_http_exception(e):
#     return {"error": True}


api.add_resource(IncomeResource, "/income")
api.add_resource(IncomeResource, "/income/<int:pk>", endpoint='delete_income')
api.add_resource(IncomeResource, "/income/<int:pk>", endpoint='update_income')

api.add_resource(ExpenseResource, "/expense")
api.add_resource(ExpenseResource, "/expense/<int:pk>", endpoint='delete_expense')

api.add_resource(ReportResource, "/report")

api.add_resource(ItemResource, "/item/<int:pk>", endpoint='update_expense')


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
