# backend/board/tests/models/test_models_item.py
import pytest
from django.core.exceptions import ValidationError

from board.models import Department, Item



# 正常系
@pytest.mark.django_db
def test_item_create_with_valid_values():
    # Arrange
    dept = Department.objects.create(name="ライン班")

    item = Item\
    (
        name="ポテトサラダセット 1 kg",
        weight_per_unit_g=1000,
        default_department=dept,
        is_department_output=True,
    )



    # Act
    item.full_clean()

    item.save()



    # Assert
    assert Item.objects.filter(pk=item.pk).exists()

    assert str(item) == "ポテトサラダセット 1 kg"



# 異常系: name の必須チェック
@pytest.mark.parametrize\
(
    "name",
    [
        None,
        "",
        " ",
        "　",
    ],
)
@pytest.mark.django_db
def test_item_name_is_required(name):
    # Arrange
    dept = Department.objects.create(name="梱包班")

    item = Item\
    (
        name=name,
        weight_per_unit_g=1000,
        default_department=dept,
        is_department_output=True,
    )

    # Act & Assert
    with pytest.raises(ValidationError):
        item.full_clean()



# 異常系: name の一意制約
@pytest.mark.django_db
def test_item_name_must_be_unique():
    # Arrange
    dept = Department.objects.create(name="梱包班")

    Item.objects.create\
    (
        name="レタス (カット) 50 g",
        weight_per_unit_g=50,
        default_department=dept,
        is_department_output=True,
    )

    dup = Item\
    (
        name="レタス (カット) 50 g",
        weight_per_unit_g=50,
        default_department=dept,
        is_department_output=True,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        dup.full_clean()



# 異常系: weight_per_unit_g は 1 以上
@pytest.mark.parametrize\
(
    "weight_per_unit_g",
    [
        None,
        0,
        -1,
    ],
)
@pytest.mark.django_db
def test_item_weight_per_unit_g_must_be_positive(weight_per_unit_g):
    # Arrange
    dept = Department.objects.create(name="梱包班")

    item = Item\
    (
        name="ポテトサラダベース 800 g",
        weight_per_unit_g=weight_per_unit_g,
        default_department=dept,
        is_department_output=True,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        item.full_clean()



# 異常系: default_department 必須
@pytest.mark.django_db
def test_item_default_department_is_required():
    # Arrange
    item = Item\
    (
        name="ポテトサラダベース 800 g",
        weight_per_unit_g=800,
        default_department=None,
        is_department_output=True,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        item.full_clean()



# 異常系: is_department_output 必須
@pytest.mark.django_db
def test_item_is_department_output_is_required():
    # Arrange
    dept = Department.objects.create(name="梱包班")

    item = Item\
    (
        name="ポテトサラダベース 800 g",
        weight_per_unit_g=800,
        default_department=dept,
        is_department_output=None,
    )



    # Act & Assert
    with pytest.raises(ValidationError):
        item.full_clean()
