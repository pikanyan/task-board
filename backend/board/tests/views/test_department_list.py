# backend/board/tests/views/test_department_list.py
import pytest

from board.models import Department



@pytest.mark.django_db
def test_get_departments_renders_table(client):
    # Arrange
    Department.objects.create(name="ライン班")
    Department.objects.create(name="いも班", uses_lot=True, lot_g=1000)



    # Act
    res = client.get("/departments/")



    # Assert
    assert res.status_code == 200



    html = res.content.decode("utf-8")

    assert "<table" in html

    assert "ライン班" in html

    assert "いも班" in html
