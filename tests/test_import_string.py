import inspect
import pytest
from machine.utils.module_loading import import_string


def test_import_all_classes():
    classes = import_string('tests.fake_classes')
    assert len(classes) == 2
    # convert list of tuples into dict so it's easier to assert
    classes_dict = dict(classes)
    assert 'tests.fake_classes:FakeA' in classes_dict
    assert inspect.isclass(classes_dict['tests.fake_classes:FakeA'])
    assert classes_dict['tests.fake_classes:FakeA'].__name__ == 'FakeA'
    assert 'tests.fake_classes:FakeB' in classes_dict
    assert inspect.isclass(classes_dict['tests.fake_classes:FakeB'])
    assert classes_dict['tests.fake_classes:FakeB'].__name__ == 'FakeB'
    assert 'fake_function' not in classes_dict


def test_import_specific_class():
    classes = import_string('tests.fake_classes.FakeA')
    assert len(classes) == 1
    assert classes[0][0] == 'tests.fake_classes:FakeA'
    assert classes[0][1].__name__ == 'FakeA'


def test_import_non_existing_module():
    with pytest.raises(ImportError) as excinfo:
        import_string('tests.fake_classes2.bla')
    assert "doesn't look like a module or class" in str(excinfo.value)
    assert "tests.fake_classes2.bla" in str(excinfo.value)


def test_import_non_existing_class():
    with pytest.raises(ImportError) as excinfo:
        import_string('tests.fake_classes.bla')
    assert "doesn't look like a module or class" in str(excinfo.value)
    assert "tests.fake_classes.bla" in str(excinfo.value)
