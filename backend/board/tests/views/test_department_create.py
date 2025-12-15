# backend/board/tests/views/test_department_create.py
import pytest

from board.models import Department



# 正常系: GET /departments/new/
@pytest.mark.django_db
def test_get_departments_new_renders_form(client):
    # Arrange



    # Act
    res = client.get("/departments/new/")



    # Assert
    assert res.status_code == 200



    html = res.content.decode("utf-8")

    assert "<form" in html

    assert 'name="name"' in html



# 正常系: POST /departments/new/
@pytest.mark.django_db
def test_post_departments_new_creates_department(client):
    # Arrange
    data = {"name": "ライン班", "uses_lot": False, "lot_g": 0}



    # Act
    res = client.post("/departments/new/", data=data)



    # Assert
    assert res.status_code in (302, 303)

    assert Department.objects.filter(name="ライン班").exists()
