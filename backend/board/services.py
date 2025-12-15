# backend/board/services.py
from collections import defaultdict
from django.db import transaction

from board import models as m




# v1 の Task 自動導出
# 時刻前倒しなし
# ロット変換なし
def derive_tasks_v1_for_due_at(due_at):
    """
    v1: due_at が一致する Order から Task を生成する
    -   ItemComponent を辿って数量を集計
    -   is_department_output=True の Item だけ Task 化
    -   due_at はそのまま使う
    """
    orders = m.Order.objects.filter(due_at=due_at)



    required = defaultdict(int)



    def accumulate(item, units):
        # 数量集計
        required[item] += units



        for c in item.components_as_parent.all():
            accumulate(c.child_item, units * c.child_units_per_parent_unit)



    for o in orders:
        accumulate(o.product_item, o.quantity_units)



    with transaction.atomic():
        # 同 due_at の Task を作り直す
        m.Task.objects.filter(due_at=due_at).delete()



        tasks = []

        for item, qty in required.items():
            if not item.is_department_output:
                continue

            tasks.append\
            (
                m.Task\
                (
                    department=item.default_department,
                    item=item,
                    quantity_units=qty,
                    due_at=due_at,
                )
            )

        m.Task.objects.bulk_create(tasks)
