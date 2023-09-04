from models import db
import io
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from repositories import ExpenseRepo


class ReportGenerator:

    def __init__(self, condition: str):
        self.setup_matplotlib()
        self.df = pd.read_sql(ExpenseRepo.get() % condition, db.engine)
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))

    @staticmethod
    def setup_matplotlib():
        matplotlib.use('Agg')

    def __call__(self):
        self.graph_sales_products("Назва", "Сума", "Назва товару", "Сума продажу", "Графік продажу товарів", 0, 0)
        self.graph_goods_balance(
            "Назва", "Залишок на складі", 'Кількість на складі', 'Назва товару',
            'Графік залишку товарів товарів', 0, 1
        )
        return self.save()

    def save(self):
        buffer = io.BytesIO()
        plt.savefig(buffer, format='pdf')
        buffer.seek(0)
        return buffer

    def graph_goods_balance(
        self,
        name_product: str,
        goods_balance: str,
        count_of_stock: str,
        xlabel: str,
        title: str,
        x: int,
        y: int
    ):
        self.axes[x, y].barh(
            self.df[name_product], self.df[goods_balance], color='skyblue',
            height=0.35, label='Поточна кількість'
        )
        self.axes[x, y].barh(
            self.df[name_product], self.df[count_of_stock], color='lightgray',
            align='edge', height=0.35, label='Кількість раніше'
        )

        self.axes[x, y].set_xlabel(xlabel)
        self.axes[x, y].set_title(title)
        self.axes[x, y].tick_params(rotation=0, axis='x')

    def graph_sales_products(
            self,
            name_product: str,
            sums: str,
            xlabel: str,
            ylabel: str,
            title: str,
            x: int,
            y: int
    ):
        self.axes[x, y].bar(self.df[name_product], self.df[sums], color='skyblue')
        self.axes[x, y].set_xlabel(xlabel)
        self.axes[x, y].set_ylabel(ylabel)
        self.axes[x, y].set_title(title)
        self.axes[x, y].tick_params(rotation=0, axis='x')


