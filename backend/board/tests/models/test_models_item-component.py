# backend/board/tests/models/test_models_item-component.py
import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from board.models import Department, Item, ItemComponent



# 正常系
@pytest.mark.django_db
def test_item_component_create_with_valid_values():
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    parent_item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    packing_dept = Department.objects.create(name="梱包班", uses_lot=False, lot_g=0)

    child_item = Item.objects.create\
    (
        name="ポテトサラダベース 800 g",
        weight_per_unit_g=800,
        default_department=packing_dept,
        is_department_output=True,
    )



    component = ItemComponent\
    (
        parent_item=parent_item,
        child_item=child_item,
        child_units_per_parent_unit=1,
    )



    # Act
    component.full_clean()

    component.save()



    # Assert
    assert ItemComponent.objects.filter(pk=component.pk).exists()



# 異常系: parent_item は必須
@pytest.mark.django_db
def test_item_component_parent_item_is_required():
    # Arrange
    packing_dept = Department.objects.create(name="梱包班", uses_lot=False, lot_g=0)

    child_item = Item.objects.create\
    (
        name="ポテトサラダベース 800 g",
        weight_per_unit_g=800,
        default_department=packing_dept,
        is_department_output=True,
    )



    component = ItemComponent\
    (
        parent_item=None,
        child_item=child_item,
        child_units_per_parent_unit=1,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        component.full_clean()



# 異常系: child_item は必須
@pytest.mark.django_db
def test_item_component_child_item_is_required():
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    parent_item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    component = ItemComponent\
    (
        parent_item=parent_item,
        child_item=None,
        child_units_per_parent_unit=1,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        component.full_clean()



# 異常系: child_units_per_parent_unit は 1 以上
@pytest.mark.django_db
@pytest.mark.parametrize\
(
    "child_units_per_parent_unit",
    
    [
        None,
        0,
        -1
    ]
)
def test_item_component_child_units_per_parent_unit_must_be_positive(child_units_per_parent_unit):
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)
    
    parent_item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    packing_dept = Department.objects.create(name="梱包班", uses_lot=False, lot_g=0)

    child_item = Item.objects.create\
    (
        name="ポテトサラダベース 800 g",
        weight_per_unit_g=800,
        default_department=packing_dept,
        is_department_output=True,
    )



    component = ItemComponent\
    (
        parent_item=parent_item,
        child_item=child_item,
        child_units_per_parent_unit=child_units_per_parent_unit,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        component.full_clean()



# 異常系: (parent_item, child_item) の組は重複禁止
@pytest.mark.django_db
def test_item_component_parent_and_child_must_be_unique():
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)
    
    parent_item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    packing_dept = Department.objects.create(name="梱包班", uses_lot=False, lot_g=0)

    child_item = Item.objects.create\
    (
        name="ポテトサラダベース 800 g",
        weight_per_unit_g=800,
        default_department=packing_dept,
        is_department_output=True,
    )



    ItemComponent.objects.create\
    (
        parent_item=parent_item,
        child_item=child_item,
        child_units_per_parent_unit=1,
    )



    # Act & Assert
    duplicate = ItemComponent\
    (
        parent_item=parent_item,
        child_item=child_item,
        child_units_per_parent_unit=2,
    )



    with pytest.raises(IntegrityError):
        duplicate.save()



# 異常系: parent_item と child_item を同一にできない
@pytest.mark.django_db
def test_item_component_parent_and_child_must_not_be_same_item():
    # Arrange
    line_dept = Department.objects.create(name="ライン班", uses_lot=False, lot_g=0)

    item = Item.objects.create\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=line_dept,
        is_department_output=True,
    )



    component = ItemComponent\
    (
        parent_item=item,
        child_item=item,
        child_units_per_parent_unit=1,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        component.full_clean()
