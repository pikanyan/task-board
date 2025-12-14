# backend/board/tests/test_app_registration.py
from django.conf import settings



def test_board_in_installed_apps():
    # Arrange
    app_label = "board"

    # Act
    installed_apps = settings.INSTALLED_APPS

    # Assert
    assert app_label in installed_apps



def test_django_tables2_in_installed_apps():
    # Arrange
    app_label = "django_tables2"

    # Act
    installed_apps = settings.INSTALLED_APPS

    # Assert
    assert app_label in installed_apps
