# backend/board/tables.py
import django_tables2 as tables

from board.models import Department



# 追加
class DepartmentTable(tables.Table):
    class Meta:
        model = Department

        fields = ("id", "name", "uses_lot", "lot_g")

        attrs = {"class": "table"}
