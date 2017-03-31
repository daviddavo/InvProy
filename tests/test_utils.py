import pytest, sys
sys.path.append('invproy/')

def test_prueba():
    import utils.logging
    assert utils.logging.return_true()

def test_run():
    import core