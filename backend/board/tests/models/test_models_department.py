# backend/board/tests/models/test_models_department.py
import pytest
from django.core.exceptions import ValidationError

from board.models import Department



# 正常系: ロット単位で管理しない班
@pytest.mark.django_db
def test_department_create_with_valid_name():
    # Arrange
    name = "ライン班"

    dept = Department(name=name)



    # Act
    dept.full_clean()

    dept.save()



    # Assert
    assert Department.objects.filter(pk=dept.pk).exists()



    assert dept.name == name

    # default 値
    assert dept.uses_lot is False

    # default 値
    assert dept.lot_g == 0



    assert str(dept) == name



# 正常系: ロット単位で管理する班の正常系
@pytest.mark.django_db
def test_department_create_with_lot_settings():
    # Arrange
    dept = Department(name="いも班", uses_lot=True, lot_g=1000)



    # Act
    dept.full_clean()

    dept.save()



    # Assert
    assert Department.objects.filter(pk=dept.pk).exists()



    assert dept.uses_lot is True

    assert dept.lot_g == 1000



# 異常系: name の必須チェック
@pytest.mark.parametrize\
(
    "name",
    [
        None,
        "",     # 空文字
        " ",    # 半角空白
        "　",   # 全角空白
    ],
)
@pytest.mark.django_db
def test_department_name_is_required(name):
    # Arrange
    dept = Department(name=name)



    # Act & Assert
    with pytest.raises(ValidationError):
        dept.full_clean()



# 異常系: uses_lot=False なのに lot_g が 0 以外
@pytest.mark.parametrize\
(
    "lot_g",
    
    [
        -1,
        1,
    ]
)
@pytest.mark.django_db
def test_department_lot_g_must_be_zero_when_uses_lot_false(lot_g):
    # Arrange
    dept = Department(name="ライン班", uses_lot=False, lot_g=lot_g)

    # Act & Assert
    with pytest.raises(ValidationError):
        dept.full_clean()



# 異常系: uses_lot=True なのに lot_g が不正
@pytest.mark.parametrize\
(
    "lot_g",

    [
        -1,
        0,
    ]
)
@pytest.mark.django_db
def test_department_lot_g_required_when_uses_lot_true(lot_g):
    # Arrange
    dept = Department(name="いも班", uses_lot=True, lot_g=lot_g)

    # Act & Assert
    with pytest.raises(ValidationError):
        dept.full_clean()
