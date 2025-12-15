# backend/board/tests/views/test_department_update.py
import pytest

from board.models import Department



# 正常系: GET /departments/{dept.id}/edit/
@pytest.mark.django_db
def test_get_department_update_renders_form(client):
    # Arrange
    dept = Department.objects.create(name="ライン班")



    # Act
    res = client.get(f"/departments/{dept.id}/edit/")



    # Assert
    assert res.status_code == 200



    html = res.content.decode("utf-8")

    assert "<form" in html

    assert "ライン班" in html



# 正常系: POST /departments/{dept.id}/edit/
@pytest.mark.django_db
def test_post_department_update_updates_department_and_redirects(client):
    # Arrange
    dept = Department.objects.create(name="ライン班")



    # Act
    res = client.post\
    (
        f"/departments/{dept.id}/edit/",

        data=
        {
            "name": "ライン班 (更新)",
            "uses_lot": False,
            "lot_g": 0,
        },
    )



    # Assert
    assert res.status_code == 302



    dept.refresh_from_db()

    assert dept.name == "ライン班 (更新)"

    assert dept.uses_lot is False

    assert dept.lot_g == 0



# 異常系: POST /departments/{dept.id}/edit/
@pytest.mark.django_db
def test_post_department_update_invalid_renders_errors(client):
    # Arrange
    dept = Department.objects.create(name="ライン班")



    # Act
    res = client.post\
    (
        f"/departments/{dept.id}/edit/",

        data=
        {
            "name": "ライン班(壊す)",
            "uses_lot": False,

            # uses_lot=False なのに 0 以外 → NG
            "lot_g": 1,
        },
    )



    # Assert
    assert res.status_code == 200



    html = res.content.decode("utf-8")

    assert "uses_lot=False の場合、lot_g は 0" in html
