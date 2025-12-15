# backend/board/tests/views/test_department_detail.py
import pytest

from board.models import Department



# 正常系
@pytest.mark.django_db
def test_get_department_detail_renders_fields(client):
    # Arrange
    dept = Department.objects.create(name="いも班", uses_lot=True, lot_g=1000)



    # Act
    res = client.get(f"/departments/{dept.pk}/")



    # Assert
    assert res.status_code == 200



    html = res.content.decode("utf-8")

    # 詳細ページに必要な情報が出ているか
    assert "いも班" in html

    assert "True" in html   # uses_lot

    assert "1000" in html   # lot_g




# 異常系: 存在しない ID でアクセス
@pytest.mark.django_db
def test_get_department_detail_returns_404_when_not_found(client):
    # Arrange

    # 存在しない ID を決め打ち
    missing_id = 999999



    # Act
    res = client.get(f"/departments/{missing_id}/")



    # Assert
    assert res.status_code == 404
