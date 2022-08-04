import re
import inspect
import pytest
from machine.asyncio.plugins.decorators import process, listen_to, respond_to, required_settings, ee, on


@pytest.fixture(scope="module")
def process_f():
    @process(slack_event_type="test_event")
    def f(event):
        pass

    return f


@pytest.fixture(scope="module")
def listen_to_f():
    @listen_to(r"hello-listen", re.IGNORECASE)
    def f(msg):
        pass

    return f


@pytest.fixture(scope="module")
def respond_to_f():
    @respond_to(r"hello-respond", re.IGNORECASE)
    def f(msg):
        pass

    return f


@pytest.fixture(scope='module')
def on_f():
    @on('test_event')
    def f(msg):
        pass

    return f


@pytest.fixture(scope="module")
def multi_decorator_f():
    @respond_to(r"hello-respond", re.IGNORECASE)
    @listen_to(r"hello-listen", re.IGNORECASE)
    def f(msg):
        pass

    return f


@pytest.fixture(scope="module")
def required_settings_list_f():
    @required_settings(["setting_1", "setting_2"])
    def f(msg):
        pass

    return f


@pytest.fixture(scope="module")
def required_settings_str_f():
    @required_settings("a_setting")
    def f(msg):
        pass

    return f


@pytest.fixture(scope="module")
def multiple_required_settings_f():
    @required_settings(["setting_1", "setting_2"])
    @required_settings("setting_3")
    def f(msg):
        pass

    return f


@pytest.fixture(scope="module")
def required_settings_class():
    @required_settings(["setting_1", "setting_2"])
    class C:
        pass

    return C


def test_process(process_f):
    assert hasattr(process_f, "metadata")
    assert hasattr(process_f.metadata, "plugin_actions")
    assert hasattr(process_f.metadata.plugin_actions, "process")
    assert process_f.metadata.plugin_actions.process == ["test_event"]


def test_listen_to(listen_to_f):
    assert hasattr(listen_to_f, "metadata")
    assert hasattr(listen_to_f.metadata, "plugin_actions")
    assert hasattr(listen_to_f.metadata.plugin_actions, "listen_to")
    assert listen_to_f.metadata.plugin_actions.listen_to == [re.compile(r"hello-listen", re.IGNORECASE)]


def test_respond_to(respond_to_f):
    assert hasattr(respond_to_f, "metadata")
    assert hasattr(respond_to_f.metadata, "plugin_actions")
    assert hasattr(respond_to_f.metadata.plugin_actions, "respond_to")
    assert respond_to_f.metadata.plugin_actions.respond_to == [re.compile(r"hello-respond", re.IGNORECASE)]


def test_mulitple_decorators(multi_decorator_f):
    assert hasattr(multi_decorator_f, "metadata")
    assert hasattr(multi_decorator_f.metadata, "plugin_actions")
    assert hasattr(multi_decorator_f.metadata.plugin_actions, "respond_to")
    assert hasattr(multi_decorator_f.metadata.plugin_actions, "listen_to")
    assert hasattr(multi_decorator_f.metadata.plugin_actions, "process")
    assert multi_decorator_f.metadata.plugin_actions.respond_to == [re.compile(r"hello-respond", re.IGNORECASE)]
    assert multi_decorator_f.metadata.plugin_actions.listen_to == [re.compile(r"hello-listen", re.IGNORECASE)]
    assert multi_decorator_f.metadata.plugin_actions.process == []


def test_on(on_f):
    assert ee.event_names() == {"test_event"}
    listeners = ee.listeners("test_event")
    assert len(listeners) == 1
    assert listeners[0] == on_f


def test_required_settings_list(required_settings_list_f):
    assert hasattr(required_settings_list_f, "metadata")
    assert hasattr(required_settings_list_f.metadata, "required_settings")
    assert isinstance(required_settings_list_f.metadata.required_settings, list)
    assert "setting_1" in required_settings_list_f.metadata.required_settings
    assert "setting_2" in required_settings_list_f.metadata.required_settings


def test_required_settings_str(required_settings_str_f):
    assert hasattr(required_settings_str_f, "metadata")
    assert hasattr(required_settings_str_f.metadata, "required_settings")
    assert isinstance(required_settings_str_f.metadata.required_settings, list)
    assert "a_setting" in required_settings_str_f.metadata.required_settings


def test_required_settings_multiple(multiple_required_settings_f):
    assert hasattr(multiple_required_settings_f, "metadata")
    assert hasattr(multiple_required_settings_f.metadata, "required_settings")
    assert isinstance(multiple_required_settings_f.metadata.required_settings, list)
    assert "setting_1" in multiple_required_settings_f.metadata.required_settings
    assert "setting_2" in multiple_required_settings_f.metadata.required_settings
    assert "setting_3" in multiple_required_settings_f.metadata.required_settings


def test_required_settings_for_class(required_settings_class):
    assert inspect.isclass(required_settings_class)
    assert hasattr(required_settings_class, "metadata")
    assert hasattr(required_settings_class.metadata, "required_settings")
    assert isinstance(required_settings_class.metadata.required_settings, list)
    assert "setting_1" in required_settings_class.metadata.required_settings
    assert "setting_2" in required_settings_class.metadata.required_settings
