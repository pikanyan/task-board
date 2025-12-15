# backend/board/tests/models/test_models_order.py
from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from board.models import Department, Item, Order



# 正常系
@pytest.mark.django_db
def test_order_create_with_valid_values():
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    product_item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    quantity_units = 3
    due_at = timezone.make_aware(datetime(2025, 12, 20, 5, 0))
    customer_name = "トライアル 天理店"

    order = Order\
    (
        product_item=product_item,
        quantity_units=quantity_units,
        due_at=due_at,
        customer_name=customer_name,
    )



    # Act
    order.full_clean()

    order.save()

    saved = Order.objects.get(pk=order.pk)



    # Assert
    assert Order.objects.filter(pk=order.pk).exists()

    assert saved.product_item == product_item
    assert saved.quantity_units == quantity_units
    assert saved.due_at == due_at
    assert saved.customer_name == customer_name



# 異常系: product_item の必須チェック
@pytest.mark.django_db
def test_order_product_item_is_required():
    # Arrange
    quantity_units = 3
    due_at = timezone.make_aware(datetime(2025, 12, 20, 5, 0))
    customer_name = "トライアル 天理店"

    order = Order\
    (
        product_item=None,
        quantity_units=quantity_units,
        due_at=due_at,
        customer_name=customer_name,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        order.full_clean()



# 異常系: quantity_units の整合性
@pytest.mark.django_db
@pytest.mark.parametrize\
(
    "quantity_units",
    [
        None,
        0,      # 0 以下
        -1,     # マイナス
    ],
)
def test_order_quantity_units_must_be_positive(quantity_units):
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    product_item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    due_at = timezone.make_aware(datetime(2025, 12, 20, 5, 0))
    customer_name = "トライアル 天理店"

    order = Order\
    (
        product_item=product_item,
        quantity_units=quantity_units,
        due_at=due_at,
        customer_name=customer_name,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        order.full_clean()


# 異常系: 納品締切日時の必須チェック
@pytest.mark.django_db
def test_order_due_at_is_required():
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    product_item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    quantity_units = 3
    due_at = None
    customer_name = "トライアル 天理店"

    order = Order\
    (
        product_item=product_item,
        quantity_units=quantity_units,
        due_at=due_at,
        customer_name=customer_name,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        order.full_clean()



# 異常系: 得意先名の必須チェック
@pytest.mark.django_db
@pytest.mark.parametrize\
(
    "customer_name",
    [
        None,
        "",     # 空文字
        " ",    # 半角空白
        "　",   # 全角空白
    ],
)
def test_order_customer_name_is_required(customer_name):
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    product_item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    quantity_units = 3
    due_at = timezone.make_aware(datetime(2025, 12, 20, 5, 0))

    order = Order\
    (
        product_item=product_item,
        quantity_units=quantity_units,
        due_at=due_at,
        customer_name=customer_name,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        order.full_clean()
