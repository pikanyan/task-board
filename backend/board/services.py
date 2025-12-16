# backend/board/services.py
from datetime import timedelta

from collections import defaultdict
from django.db import transaction

from board import models as m




########## v1 と v2 の共通関数 ##########

def _accumulate_required_v1(required_by_id, item, units):
    # NOTE: v1 は再帰で components を辿るため、将来 N+1 になり得る

    """
    ポテトサラダセット 1 kg 5
        ポテトサラダベース 800 g 5
            じゃがいも (マッシュ) 550 g 5
                じゃがいも (乱切り) 550 g 5
            人参 (いちょう切り) 80 g 5
            きゅうり (小口切り) 70 g 5
            ハム (短冊切り) 100 g 5
        レタス (カット) 50 g 10
        赤玉ねぎ (スライス) 50 g 10
    """
    required_by_id[item.id] += units



    # item を親として参照している
    # 全ての ItemComponent インスタンス

    # item は Item インスタンス
    # component は ItemComponent インスタンス
    for c in item.components_as_parent.all():
        _accumulate_required_v1\
        (
            required_by_id,
            c.child_item,
            units * c.child_units_per_parent_unit,
        )



########## v2 ##########

"""
python manage.py shell



from datetime import datetime, timezone

from board.services import derive_tasks_v2_for_due_at



# fixtures の Order(due_at) に合わせる
due_at = datetime(2025, 12, 20, 5, 0, tzinfo=timezone.utc)

# Order + ItemComponent から Task を再生成する (v2)
derive_tasks_v2_for_due_at(due_at)



exit()
"""




# 部署ごとの 1 個あたり処理時間 (秒)
DEPARTMENT_SPEED_SEC =\
{
    "入荷班": 60,
    "いも班": 60,
    "大葉班": 60,
    "梱包班": 60,
    "ライン班": 60,
}


# 工程レベル 
# 数字が大きいほど後工程 = ラインに近い
DEPARTMENT_STAGE =\
{
    "入荷班": 0,
    "いも班": 1,
    "大葉班": 1,
    "梱包班": 2,
    "ライン班": 3,
}

MAX_STAGE = 3       # ライン班

STAGE_MINUTES = 5   # 1 ステージ差あたり 5 分前倒し



# due_at 前倒し
def calc_task_due_at(department, quantity_units, base_due_at):
    sec_per_unit = DEPARTMENT_SPEED_SEC.get(department.name)


    # 未定義の部署はそのまま
    if sec_per_unit is None:
        return base_due_at



    # 1) 個数に応じた処理時間
    work_sec = sec_per_unit * quantity_units


    # 2) 工程レベルに応じたバッファ 
    # ラインより前ほど早く終わらせる
    stage = DEPARTMENT_STAGE.get(department.name, MAX_STAGE)



    # ライン班との差
    stage_diff = MAX_STAGE - stage

    stage_sec = stage_diff * STAGE_MINUTES * 60

    return base_due_at - timedelta(seconds=(work_sec + stage_sec))




# ToDo
# このようにハードコードせず
# DB テーブルに出力し
# 管理画面から編集できるようにする

# 小アイテム名 -> ロット品名 (対応付け)
SMALL_TO_BULK_NAME =\
{
    "じゃがいも (乱切り) 550 g": "じゃがいも (乱切り) 1 kg",
    "レタス (カット) 50 g": "レタス (カット) 1 kg",
    "赤玉ねぎ (スライス) 50 g": "赤玉ねぎ (スライス) 1 kg",
    "人参 (いちょう切り) 80 g": "人参 (いちょう切り) 1 kg",
    "きゅうり (小口切り) 70 g": "きゅうり (小口切り) 1 kg",
    "ハム (短冊切り) 100 g": "ハム (短冊切り) 1 kg",
}



# v2 の Task 自動導出 
# ロット変換 + 前倒し
def derive_tasks_v2_for_due_at(due_at):
    """
    v2:
    -   v1 と同じ集計 (ItemComponent を辿る)
    -   is_department_output=True を Task 化
    -   Department.uses_lot=True の部署は、小アイテム(g)を 1kg ロット品に切り上げて Task 化
    -   due_at は calc_task_due_at で前倒し
    """
    orders = m.Order.objects.filter(due_at=due_at).select_related("product_item")

    required_by_id = defaultdict(int)

    for o in orders:
        _accumulate_required_v1(required_by_id, o.product_item, o.quantity_units)

    item_ids = list(required_by_id.keys())

    items_by_id =\
    {
        i.id: i

        for i in m.Item.objects.filter(id__in=item_ids).select_related("default_department")
    }

    # 小 -> ロット品をまとめて引く (N+1 回避)
    bulk_names = []

    for item_id in item_ids:
        it = items_by_id.get(item_id)

        if it is None:
            continue

        bn = SMALL_TO_BULK_NAME.get(it.name)

        if bn:
            bulk_names.append(bn)

    bulk_by_name =\
    {
        i.name: i

        for i in m.Item.objects.filter(name__in=bulk_names).select_related("default_department")
    }



    # bulk_item_id -> 合計 g
    bulk_total_g_by_id = defaultdict(int)

    for item_id, qty_units in required_by_id.items():
        small = items_by_id.get(item_id)

        if small is None:
            continue



        bn = SMALL_TO_BULK_NAME.get(small.name)

        if not bn:
            continue


        bulk = bulk_by_name.get(bn)

        if bulk is None:
            continue


        bulk_total_g_by_id[bulk.id] += qty_units * small.weight_per_unit_g



    with transaction.atomic():
        # v2 は同 due_at を作り直す
        m.Task.objects.filter(due_at=due_at).delete()

        tasks = []



        # 通常 Task (前倒し)
        for item_id, qty in required_by_id.items(): 
            item = items_by_id.get(item_id)

            if item is None:
                continue


            if not item.is_department_output:
                continue


            dept = item.default_department

            task_due_at = calc_task_due_at(dept, qty, due_at)

            tasks.append\
            (
                m.Task(department=dept, item=item, quantity_units=qty, due_at=task_due_at)
            )



        # ロット Task (Department の lot_g で切り上げ)
        for bulk_item_id, total_g in bulk_total_g_by_id.items():
            bulk_item = m.Item.objects.select_related("default_department").get(id=bulk_item_id)

            dept = bulk_item.default_department



            if not getattr(dept, "uses_lot", False):
                continue



            lot_g = getattr(dept, "lot_g", 1000) or 1000

            lots = (total_g + lot_g - 1) // lot_g

            if lots <= 0:
                continue



            task_due_at = calc_task_due_at(dept, lots, due_at)

            tasks.append\
            (
                m.Task(department=dept, item=bulk_item, quantity_units=lots, due_at=task_due_at)
            )



        m.Task.objects.bulk_create(tasks)


# 全 due_at を v2 で再生成
def rebuild_all_tasks_from_orders_v2():
    with transaction.atomic():
        m.Task.objects.all().delete()

        due_ats = m.Order.objects.values_list("due_at", flat=True).distinct()

        for due_at in due_ats:
            derive_tasks_v2_for_due_at(due_at)



########## v1 ##########

"""
python manage.py shell



from datetime import datetime, timezone

from board.services import derive_tasks_v1_for_due_at



due_at = datetime(2025, 12, 20, 5, 0, tzinfo=timezone.utc)

derive_tasks_v1_for_due_at(due_at)



exit()
"""





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



    # 全ての Order から、必要数量を集計していく
    for o in orders:
        # ポテトサラダセット 1 kg x 3 @ 2025-12-20 05:00:00+00:00 (トライアル 天理店)
        # ポテトサラダセット 1 kg x 2 @ 2025-12-20 05:00:00+00:00 (オークワ 田原本店)
        # print(order)

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
