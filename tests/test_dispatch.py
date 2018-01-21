import re

import pytest
from apscheduler.schedulers.base import BaseScheduler

from machine.slack import MessagingClient
from machine.dispatch import EventDispatcher
from machine.plugins.base import Message
from machine.storage.backends.base import MachineBaseStorage
from tests.fake_plugins import FakePlugin, FakePlugin2


@pytest.fixture
def msg_client(mocker):
    return mocker.MagicMock(spec=MessagingClient)

@pytest.fixture
def storage(mocker):
    return mocker.MagicMock(spec=MachineBaseStorage)

@pytest.fixture
def fake_plugin(mocker, msg_client, storage):
    plugin_instance = FakePlugin({}, msg_client, storage)
    mocker.spy(plugin_instance, 'respond_function')
    mocker.spy(plugin_instance, 'listen_function')
    mocker.spy(plugin_instance, 'process_function')
    return plugin_instance

@pytest.fixture
def fake_plugin2(mocker, msg_client, storage):
    plugin_instance = FakePlugin2({}, msg_client, storage)
    mocker.spy(plugin_instance, 'catch_all')
    return plugin_instance

@pytest.fixture
def plugin_actions(fake_plugin, fake_plugin2):
    respond_fn = getattr(fake_plugin, 'respond_function')
    listen_fn = getattr(fake_plugin, 'listen_function')
    process_fn = getattr(fake_plugin, 'process_function')
    catch_all_fn = getattr(fake_plugin2, 'catch_all')
    plugin_actions = {
        'catch_all': {
            'TestPlugin2': {
                'class': fake_plugin2,
                'class_name': 'tests.fake_plugins.FakePlugin2',
                'function': catch_all_fn
            }
        },
        'listen_to': {
            'TestPlugin.listen_function-hi': {
                'class': fake_plugin,
                'class_name': 'tests.fake_plugins.FakePlugin',
                'function': listen_fn,
                'regex': re.compile('hi', re.IGNORECASE)
            }
        },
        'respond_to': {
            'TestPlugin.respond_function-hello': {
                'class': fake_plugin,
                'class_name': 'tests.fake_plugins.FakePlugin',
                'function': respond_fn,
                'regex': re.compile('hello', re.IGNORECASE)
            }
        },
        'process': {
            'some_event': {
                'TestPlugin.process_function': {
                    'class': fake_plugin,
                    'class_name': 'tests.fake_plugins.FakePlugin',
                    'function': process_fn
                }
            }
        }
    }
    return plugin_actions

@pytest.fixture
def dispatcher(mocker, plugin_actions):
    mocker.patch('machine.dispatch.ThreadPool', autospec=True)
    mocker.patch('machine.singletons.SlackClient', autospec=True)
    mocker.patch('machine.singletons.BackgroundScheduler', autospec=True)
    dispatch_instance = EventDispatcher(plugin_actions)
    mocker.patch.object(dispatch_instance, '_get_bot_id')
    dispatch_instance._get_bot_id.return_value = '123'
    mocker.patch.object(dispatch_instance, '_get_bot_name')
    dispatch_instance._get_bot_name.return_value = 'superbot'
    return dispatch_instance

def test_handle_event_process(dispatcher, fake_plugin):
    some_event = {'type': 'some_event'}
    dispatcher.handle_event(some_event)
    assert fake_plugin.process_function.call_count == 1
    fake_plugin.process_function.assert_called_once_with(some_event)


def test_handle_event_catch_all(dispatcher, fake_plugin2):
    any_event = {'type': 'foobar'}
    dispatcher.handle_event(any_event)
    fake_plugin2.catch_all.assert_called_once_with(any_event)

def _assert_message(args, text):
    # called with 1 positional arg and 0 kw args
    assert len(args[0]) == 1
    assert len(args[1]) == 0
    # assert called with Message
    assert isinstance(args[0][0], Message)
    # assert message equals expected text
    assert args[0][0].text == text

def test_handle_event_listen_to(dispatcher, fake_plugin, fake_plugin2):
    msg_event = {'type': 'message', 'text': 'hi', 'channel': 'C1', 'user': 'user1'}
    dispatcher.handle_event(msg_event)
    fake_plugin2.catch_all.assert_called_once_with(msg_event)
    assert fake_plugin.listen_function.call_count == 1
    assert fake_plugin.respond_function.call_count == 0
    args = fake_plugin.listen_function.call_args
    _assert_message(args, 'hi')

def test_handle_event_respond_to(dispatcher, fake_plugin, fake_plugin2):
    msg_event = {'type': 'message', 'text': '<@123> hello', 'channel': 'C1', 'user': 'user1'}
    dispatcher.handle_event(msg_event)
    fake_plugin2.catch_all.assert_called_once_with(msg_event)
    assert fake_plugin.respond_function.call_count == 1
    assert fake_plugin.listen_function.call_count == 0
    args = fake_plugin.respond_function.call_args
    _assert_message(args, 'hello')

def test_check_bot_mention(dispatcher):
    normal_msg_event = {'text': 'hi', 'channel': 'C1'}
    event = dispatcher._check_bot_mention(normal_msg_event)
    assert event == None

    mention_msg_event = {'text': '<@123> hi', 'channel': 'C1'}
    event = dispatcher._check_bot_mention(mention_msg_event)
    assert event == {'text': 'hi', 'channel': 'C1'}

    mention_msg_event_username = {'text': 'superbot: hi', 'channel': 'C1'}
    event = dispatcher._check_bot_mention(mention_msg_event_username)
    assert event == {'text': 'hi', 'channel': 'C1'}

    mention_msg_event_group = {'text': '<@123> hi', 'channel': 'G1'}
    event = dispatcher._check_bot_mention(mention_msg_event_group)
    assert event == {'text': 'hi', 'channel': 'G1'}

    mention_msg_event_other_user = {'text': '<@456> hi', 'channel': 'C1'}
    event = dispatcher._check_bot_mention(mention_msg_event_other_user)
    assert event == None

    mention_msg_event_dm = {'text': 'hi', 'channel': 'D1'}
    event = dispatcher._check_bot_mention(mention_msg_event_dm)
    assert event == {'text': 'hi', 'channel': 'D1'}