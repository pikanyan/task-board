# backend/board/tests/services/test_task_derive_v1.py
from datetime import datetime, timezone as dt_timezone

from django.test import TestCase

from board import models as m
from board.services import derive_tasks_v1_for_due_at



class TestTaskDeriveV1(TestCase):
    def test_1_order_derives_expected_tasks(self):
        # Arrange
        line = m.Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

        pack = m.Department.objects.create(name="梱包班", uses_lot=False, lot_g=0)



        salad = m.Item.objects.create\
        (
            name="ポテトサラダセット 1 kg",
            weight_per_unit_g=1000,
            default_department=line,
            is_department_output=True,
        )



        base = m.Item.objects.create\
        (
            name="ポテトサラダベース 800 g",
            weight_per_unit_g=800,
            default_department=pack,
            is_department_output=True,
        )

        lettuce = m.Item.objects.create\
        (
            name="レタス (カット) 50 g",
            weight_per_unit_g=50,
            default_department=pack,
            is_department_output=True,
        )

        onion = m.Item.objects.create\
        (
            name="赤玉ねぎ (スライス) 50 g",
            weight_per_unit_g=50,
            default_department=pack,
            is_department_output=True,
        )



        m.ItemComponent.objects.create(parent_item=salad, child_item=base, child_units_per_parent_unit=1)
        m.ItemComponent.objects.create(parent_item=salad, child_item=lettuce, child_units_per_parent_unit=2)
        m.ItemComponent.objects.create(parent_item=salad, child_item=onion, child_units_per_parent_unit=2)



        due_at = datetime(2025, 12, 20, 5, 0, tzinfo=dt_timezone.utc)

        m.Order.objects.create(product_item=salad, quantity_units=3, due_at=due_at, customer_name="トライアル 天理店")




        # Act
        derive_tasks_v1_for_due_at(due_at)



        # Assert
        got =\
        {
            (t.department.name, t.item.name): t.quantity_units
            
            for t
            
            in m.Task.objects.all()
        }

        self.assertEqual(got[("ライン班", "ポテトサラダセット 1 kg")], 3)

        self.assertEqual(got[("梱包班", "ポテトサラダベース 800 g")], 3)
        self.assertEqual(got[("梱包班", "レタス (カット) 50 g")], 6)
        self.assertEqual(got[("梱包班", "赤玉ねぎ (スライス) 50 g")], 6)




    def test_2_orders_are_aggregated(self):
        # Arrange
        line = m.Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)
        pack = m.Department.objects.create(name="梱包班", uses_lot=False, lot_g=0)



        salad = m.Item.objects.create\
        (
            name="ポテトサラダセット 1 kg",
            weight_per_unit_g=1000,
            default_department=line,
            is_department_output=True,
        )

        lettuce = m.Item.objects.create\
        (
            name="レタス (カット) 50 g",
            weight_per_unit_g=50,
            default_department=pack,
            is_department_output=True,
        )



        m.ItemComponent.objects.create(parent_item=salad, child_item=lettuce, child_units_per_parent_unit=2)



        due_at = datetime(2025, 12, 20, 5, 0, tzinfo=dt_timezone.utc)

        m.Order.objects.create(product_item=salad, quantity_units=1, due_at=due_at, customer_name="A店")
        m.Order.objects.create(product_item=salad, quantity_units=2, due_at=due_at, customer_name="B店")



        # Act
        derive_tasks_v1_for_due_at(due_at)



        # Assert
        t_parent = m.Task.objects.get(item=salad)

        t_child = m.Task.objects.get(item=lettuce)



        self.assertEqual(t_parent.quantity_units, 3)

        self.assertEqual(t_child.quantity_units, 6)
