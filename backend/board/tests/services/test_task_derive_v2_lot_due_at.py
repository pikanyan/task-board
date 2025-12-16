# backend/board/tests/services/test_task_derive_v2_lot_due_at.py
from datetime import datetime, timezone as dt_timezone

from django.test import TestCase

from board import models as m
from board.services import derive_tasks_v2_for_due_at, calc_task_due_at



class TestTaskDeriveV2LotDueAt(TestCase):
    def test_orders_derive_lot_tasks_and_shift_due_at(self):
        # Arrange
        inbound = m.Department.objects.create(name="入荷班", uses_lot=True, lot_g=1000)
        imo = m.Department.objects.create(name="いも班", uses_lot=True, lot_g=1000)
        ooba = m.Department.objects.create(name="大葉班", uses_lot=True, lot_g=1000)
        pack = m.Department.objects.create(name="梱包班", uses_lot=False, lot_g=0)
        line = m.Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

        salad = m.Item.objects.create(name="ポテトサラダセット 1 kg", weight_per_unit_g=1000, default_department=line, is_department_output=True)
        base = m.Item.objects.create(name="ポテトサラダベース 800 g", weight_per_unit_g=800, default_department=pack, is_department_output=True)
        lettuce50 = m.Item.objects.create(name="レタス (カット) 50 g", weight_per_unit_g=50, default_department=pack, is_department_output=True)
        onion50 = m.Item.objects.create(name="赤玉ねぎ (スライス) 50 g", weight_per_unit_g=50, default_department=pack, is_department_output=True)

        mash550 = m.Item.objects.create(name="じゃがいも (マッシュ) 550 g", weight_per_unit_g=550, default_department=pack, is_department_output=False)
        carrot80 = m.Item.objects.create(name="人参 (いちょう切り) 80 g", weight_per_unit_g=80, default_department=pack, is_department_output=False)
        cucumber70 = m.Item.objects.create(name="きゅうり (小口切り) 70 g", weight_per_unit_g=70, default_department=pack, is_department_output=False)
        ham100 = m.Item.objects.create(name="ハム (短冊切り) 100 g", weight_per_unit_g=100, default_department=pack, is_department_output=False)
        potato550 = m.Item.objects.create(name="じゃがいも (乱切り) 550 g", weight_per_unit_g=550, default_department=pack, is_department_output=False)

        lettuce1k = m.Item.objects.create(name="レタス (カット) 1 kg", weight_per_unit_g=1000, default_department=ooba, is_department_output=True)
        onion1k = m.Item.objects.create(name="赤玉ねぎ (スライス) 1 kg", weight_per_unit_g=1000, default_department=ooba, is_department_output=True)
        potato1k = m.Item.objects.create(name="じゃがいも (乱切り) 1 kg", weight_per_unit_g=1000, default_department=imo, is_department_output=True)
        carrot1k = m.Item.objects.create(name="人参 (いちょう切り) 1 kg", weight_per_unit_g=1000, default_department=ooba, is_department_output=True)
        cucumber1k = m.Item.objects.create(name="きゅうり (小口切り) 1 kg", weight_per_unit_g=1000, default_department=ooba, is_department_output=True)
        ham1k = m.Item.objects.create(name="ハム (短冊切り) 1 kg", weight_per_unit_g=1000, default_department=inbound, is_department_output=True)



        m.ItemComponent.objects.create(parent_item=salad, child_item=base, child_units_per_parent_unit=1)
        m.ItemComponent.objects.create(parent_item=salad, child_item=lettuce50, child_units_per_parent_unit=2)
        m.ItemComponent.objects.create(parent_item=salad, child_item=onion50, child_units_per_parent_unit=2)

        m.ItemComponent.objects.create(parent_item=base, child_item=mash550, child_units_per_parent_unit=1)
        m.ItemComponent.objects.create(parent_item=base, child_item=carrot80, child_units_per_parent_unit=1)
        m.ItemComponent.objects.create(parent_item=base, child_item=cucumber70, child_units_per_parent_unit=1)
        m.ItemComponent.objects.create(parent_item=base, child_item=ham100, child_units_per_parent_unit=1)

        m.ItemComponent.objects.create(parent_item=mash550, child_item=potato550, child_units_per_parent_unit=1)



        due_at = datetime(2025, 12, 20, 5, 0, tzinfo=dt_timezone.utc)

        m.Order.objects.create(product_item=salad, quantity_units=3, due_at=due_at, customer_name="トライアル 天理店")
        m.Order.objects.create(product_item=salad, quantity_units=2, due_at=due_at, customer_name="オークワ 田原本店")



        # Act
        derive_tasks_v2_for_due_at(due_at)



        # Assert
        def qty(item_name: str) -> int:
            return m.Task.objects.get(item__name=item_name).quantity_units



        self.assertEqual(qty("ポテトサラダセット 1 kg"), 5)
        self.assertEqual(qty("ポテトサラダベース 800 g"), 5)
        self.assertEqual(qty("レタス (カット) 50 g"), 10)
        self.assertEqual(qty("赤玉ねぎ (スライス) 50 g"), 10)



        # ロット変換 (合計 g から 1 kg ロットに切り上げ)
        self.assertEqual(qty("じゃがいも (乱切り) 1 kg"), 3)    # 550g * 5 = 2750g -> 3
        self.assertEqual(qty("レタス (カット) 1 kg"), 1)        # 50g * 10 = 500g -> 1
        self.assertEqual(qty("赤玉ねぎ (スライス) 1 kg"), 1)    # 50g * 10 = 500g -> 1
        self.assertEqual(qty("人参 (いちょう切り) 1 kg"), 1)    # 80g * 5 = 400g -> 1
        self.assertEqual(qty("きゅうり (小口切り) 1 kg"), 1)    # 70g * 5 = 350g -> 1
        self.assertEqual(qty("ハム (短冊切り) 1 kg"), 1)        # 100g * 5 = 500g -> 1



        # due_at 前倒し (calc_task_due_at と一致すること)
        t = m.Task.objects.get(item__name="じゃがいも (乱切り) 1 kg")

        self.assertEqual(t.due_at, calc_task_due_at(imo, 3, due_at))
