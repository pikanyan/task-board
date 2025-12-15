# backend/board/tests/admin/test_admin_registered_models.py
import pytest

from django.contrib.admin import site

from board import models



@pytest.mark.parametrize\
(
    "model",
    [
        models.Department,
        models.Item,
        models.ItemComponent,
        models.Order,
    ],
)
def test_admin_registers_board_models(model):
    # Arrange



    # Act
    is_registered = model in site._registry



    # Assert
    assert is_registered
