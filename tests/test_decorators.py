import re
import inspect
import pytest
from blinker import signal
from machine.plugins.decorators import process, listen_to, respond_to, schedule, on, \
    required_settings, route


@pytest.fixture(scope='module')
def process_f():
    @process(slack_event_type='test_event')
    def f(event):
        pass

    return f


@pytest.fixture(scope='module')
def listen_to_f():
    @listen_to(r'hello', re.IGNORECASE)
    def f(msg):
        pass

    return f


@pytest.fixture(scope='module')
def respond_to_f():
    @respond_to(r'hello', re.IGNORECASE)
    def f(msg):
        pass

    return f


@pytest.fixture(scope='module')
def schedule_f():
    @schedule(hour='*/2', minute=30)
    def f():
        pass

    return f


@pytest.fixture(scope='module')
def multi_decorator_f():
    @respond_to(r'hello', re.IGNORECASE)
    @listen_to(r'hello', re.IGNORECASE)
    def f(msg):
        pass

    return f


@pytest.fixture(scope='module')
def on_f():
    @on('test_event')
    def f(msg):
        pass

    return f


@pytest.fixture(scope='module')
def required_settings_list_f():
    @required_settings(['setting_1', 'setting_2'])
    def f(msg):
        pass

    return f


@pytest.fixture(scope='module')
def required_settings_str_f():
    @required_settings('a_setting')
    def f(msg):
        pass

    return f


@pytest.fixture(scope='module')
def multiple_required_settings_f():
    @required_settings(['setting_1', 'setting_2'])
    @required_settings('setting_3')
    def f(msg):
        pass

    return f


@pytest.fixture(scope='module')
def required_settings_class():
    @required_settings(['setting_1', 'setting_2'])
    class C:
        pass

    return C

@pytest.fixture(scope='module')
def route_f():
    @route('/test', method='POST')
    def f():
        pass
    return f


def test_process(process_f):
    assert hasattr(process_f, 'metadata')
    assert 'plugin_actions' in process_f.metadata
    assert 'process' in process_f.metadata['plugin_actions']
    assert 'event_type' in process_f.metadata['plugin_actions']['process']
    assert process_f.metadata['plugin_actions']['process']['event_type'] == 'test_event'


def test_listen_to(listen_to_f):
    assert hasattr(listen_to_f, 'metadata')
    assert 'plugin_actions' in listen_to_f.metadata
    assert 'listen_to' in listen_to_f.metadata['plugin_actions']
    assert 'regex' in listen_to_f.metadata['plugin_actions']['listen_to']
    assert listen_to_f.metadata['plugin_actions']['listen_to']['regex'] == [
        re.compile(r'hello', re.IGNORECASE)]


def test_respond_to(respond_to_f):
    assert hasattr(respond_to_f, 'metadata')
    assert 'plugin_actions' in respond_to_f.metadata
    assert 'respond_to' in respond_to_f.metadata['plugin_actions']
    assert 'regex' in respond_to_f.metadata['plugin_actions']['respond_to']
    assert respond_to_f.metadata['plugin_actions']['respond_to']['regex'] == [
        re.compile(r'hello', re.IGNORECASE)]


def test_schedule(schedule_f):
    assert hasattr(schedule_f, 'metadata')
    assert 'plugin_actions' in schedule_f.metadata
    assert 'schedule' in schedule_f.metadata['plugin_actions']
    assert schedule_f.metadata['plugin_actions']['schedule']['hour'] == '*/2'
    assert schedule_f.metadata['plugin_actions']['schedule']['minute'] == 30


def test_mulitple_decorators(multi_decorator_f):
    assert hasattr(multi_decorator_f, 'metadata')
    assert 'plugin_actions' in multi_decorator_f.metadata
    assert 'respond_to' in multi_decorator_f.metadata['plugin_actions']
    assert 'listen_to' in multi_decorator_f.metadata['plugin_actions']
    assert 'process' not in multi_decorator_f.metadata['plugin_actions']


def test_on(on_f):
    e = signal('test_event')
    assert bool(e.receivers)


def test_required_settings_list(required_settings_list_f):
    assert hasattr(required_settings_list_f, 'metadata')
    assert 'required_settings' in required_settings_list_f.metadata
    assert isinstance(required_settings_list_f.metadata['required_settings'], list)
    assert 'setting_1' in required_settings_list_f.metadata['required_settings']
    assert 'setting_2' in required_settings_list_f.metadata['required_settings']


def test_required_settings_str(required_settings_str_f):
    assert hasattr(required_settings_str_f, 'metadata')
    assert 'required_settings' in required_settings_str_f.metadata
    assert isinstance(required_settings_str_f.metadata['required_settings'], list)
    assert 'a_setting' in required_settings_str_f.metadata['required_settings']


def test_required_settings_multiple(multiple_required_settings_f):
    assert hasattr(multiple_required_settings_f, 'metadata')
    assert 'required_settings' in multiple_required_settings_f.metadata
    assert isinstance(multiple_required_settings_f.metadata['required_settings'], list)
    assert 'setting_1' in multiple_required_settings_f.metadata['required_settings']
    assert 'setting_2' in multiple_required_settings_f.metadata['required_settings']
    assert 'setting_3' in multiple_required_settings_f.metadata['required_settings']


def test_required_settings_for_class(required_settings_class):
    assert inspect.isclass(required_settings_class)
    assert hasattr(required_settings_class, 'metadata')
    assert 'required_settings' in required_settings_class.metadata
    assert isinstance(required_settings_class.metadata['required_settings'], list)
    assert 'setting_1' in required_settings_class.metadata['required_settings']
    assert 'setting_2' in required_settings_class.metadata['required_settings']


def test_route(route_f):
    assert hasattr(route_f, 'metadata')
    assert 'plugin_actions' in route_f.metadata
    assert 'route' in route_f.metadata['plugin_actions']
    assert len(route_f.metadata['plugin_actions']['route']) == 1
    assert route_f.metadata['plugin_actions']['route'][0]['path'] == '/test'
    assert route_f.metadata['plugin_actions']['route'][0]['method'] == 'POST'
