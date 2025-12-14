# backend/board/tests/test_app_skeleton.py
import importlib



def test_board_module_is_importable():
    # Arrange
    module_name = "board.apps"



    # Act
    
    # startapp していないと、ここで ModuleNotFoundError になる
    apps_module = importlib.import_module(module_name)



    # Assert
    assert hasattr(apps_module, "BoardConfig")
