# backend/board/tests/views/test_department_delete.py
import pytest

from board.models import Department



@pytest.mark.django_db
def test_post_department_delete_deletes_and_redirects(client):
    # Arrange
    dept = Department.objects.create(name="ライン班")



    # Act
    res = client.post(f"/departments/{dept.id}/delete/")



    # Assert
    assert res.status_code == 302

    assert res["Location"] == "/departments/"

    assert Department.objects.filter(id=dept.id).exists() is False
