# backend/board/services.py
from collections import defaultdict
from django.db import transaction

from board import models as m



"""
python manage.py shell



from datetime import datetime, timezone

from board.services import derive_tasks_v1_for_due_at



due_at = datetime(2025, 12, 20, 5, 0, tzinfo=timezone.utc)

derive_tasks_v1_for_due_at(due_at)



exit()
"""



def _accumulate_required_v1(required_by_id, item, units):
    # NOTE: v1 は再帰で components を辿るため、将来 N+1 になり得る
    required_by_id[item.id] += units



    for c in item.components_as_parent.all():
        _accumulate_required_v1\
        (
            required_by_id,
            c.child_item,
            units * c.child_units_per_parent_unit,
        )



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



    required_by_id = defaultdict(int)



    for o in orders:
        # 数量集計
        _accumulate_required_v1(required_by_id, o.product_item, o.quantity_units)



    item_ids = list(required_by_id.keys())

    # id -> Item を一括取得
    # default_department もまとめて取る
    items_by_id =\
    {
        i.id: i

        for i
        
        in m.Item.objects.filter(id__in=item_ids).select_related("default_department")
    }



    with transaction.atomic():
        # 同 due_at の Task を作り直す
        m.Task.objects.filter(due_at=due_at).delete()



        tasks = []

        for item_id, qty in required_by_id.items():
            item = items_by_id.get(item_id)



            # 念のためスキップ
            if item is None:
                continue


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



        # まとめて登録
        m.Task.objects.bulk_create(tasks)
