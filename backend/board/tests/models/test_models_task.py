# backend/board/tests/models/test_models_task.py
from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from board.models import Department, Item, Task



# 正常系
@pytest.mark.django_db
def test_task_create_with_valid_values():
    # Arrange
    department = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=department,
        is_department_output=True,
    )



    quantity_units = 5

    due_at = timezone.make_aware(datetime(2025, 12, 20, 5, 0))

    task = Task\
    (
        department=department,
        item=item,
        quantity_units=quantity_units,
        due_at=due_at,
    )



    # Act
    task.full_clean()

    task.save()

    saved = Task.objects.get(pk=task.pk)



    # Assert
    assert Task.objects.filter(pk=task.pk).exists()

    assert saved.department == department
    assert saved.item == item
    assert saved.quantity_units == quantity_units
    assert saved.due_at == due_at



# 異常系: department の必須チェック
@pytest.mark.django_db
def test_task_department_is_required():
    # Arrange
    department = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=department,
        is_department_output=True,
    )

    task = Task\
    (
        department=None,
        item=item,
        quantity_units=5,
        due_at=timezone.make_aware(datetime(2025, 12, 20, 5, 0)),
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        task.full_clean()



# 異常系: item の必須チェック
@pytest.mark.django_db
def test_task_item_is_required():
    # Arrange
    department = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    quantity_units = 5
    
    due_at = timezone.make_aware(datetime(2025, 12, 20, 5, 0))

    task = Task\
    (
        department=department,
        item=None,
        quantity_units=quantity_units,
        due_at=due_at,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        task.full_clean()



# 異常系: quantity_units の整合性
@pytest.mark.django_db
@pytest.mark.parametrize\
(
    "quantity_units",
    [
        None,
        0,      # 0 以下
        -1      # マイナス
    ],
)
def test_task_quantity_units_must_be_positive(quantity_units):
    # Arrange
    department = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    item = Item.objects.create\
    (
        name="カレー用野菜セット 1 kg",
        weight_per_unit_g=1000,
        default_department=department,
        is_department_output=True,
    )

    due_at = timezone.make_aware(datetime(2025, 12, 20, 5, 0))

    task = Task\
    (
        department=department,
        item=item,
        quantity_units=quantity_units,
        due_at=due_at,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        task.full_clean()



# 異常系: due_at の必須チェック
@pytest.mark.django_db
def test_task_due_at_is_required():
    # Arrange
    department = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=department,
        is_department_output=True,
    )

    quantity_units = 5

    task = Task\
    (
        department=department,
        item=item,
        quantity_units=quantity_units,
        due_at=None,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        task.full_clean()
