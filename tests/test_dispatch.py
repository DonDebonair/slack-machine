import re

import pytest

from machine.clients.slack import SlackClient
from machine.dispatch import EventDispatcher
from machine.plugins.base import Message
from machine.storage.backends.base import MachineBaseStorage
from machine.utils.collections import CaseInsensitiveDict
from tests.fake_plugins import FakePlugin


@pytest.fixture
def msg_client(mocker):
    return mocker.MagicMock(spec=SlackClient)


@pytest.fixture
def storage(mocker):
    return mocker.MagicMock(spec=MachineBaseStorage)


@pytest.fixture
def fake_plugin(mocker, msg_client, storage):
    plugin_instance = FakePlugin(msg_client, CaseInsensitiveDict(), storage)
    mocker.spy(plugin_instance, 'respond_function')
    mocker.spy(plugin_instance, 'listen_function')
    mocker.spy(plugin_instance, 'process_function')
    return plugin_instance


@pytest.fixture
def plugin_actions(fake_plugin):
    respond_fn = getattr(fake_plugin, 'respond_function')
    listen_fn = getattr(fake_plugin, 'listen_function')
    process_fn = getattr(fake_plugin, 'process_function')
    plugin_actions = {
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


@pytest.fixture(params=[None, {"ALIASES": "!"}, {"ALIASES": "!,$"}], ids=["No Alias", "Alias", "Aliases"])
def dispatcher(mocker, plugin_actions, request):
    mocker.patch('machine.dispatch.LowLevelSlackClient', autospec=True)
    dispatch_instance = EventDispatcher(plugin_actions, request.param)
    mocker.patch.object(dispatch_instance, '_get_bot_id')
    dispatch_instance._get_bot_id.return_value = '123'
    mocker.patch.object(dispatch_instance, '_get_bot_name')
    dispatch_instance._get_bot_name.return_value = 'superbot'
    dispatch_instance._aliases = request.param
    return dispatch_instance


def _assert_message(args, text):
    # called with 1 positional arg and 0 kw args
    assert len(args[0]) == 1
    assert len(args[1]) == 0
    # assert called with Message
    assert isinstance(args[0][0], Message)
    # assert message equals expected text
    assert args[0][0].text == text


def test_handle_event_listen_to(dispatcher, fake_plugin):
    msg_event = {'data': {'type': 'message', 'text': 'hi', 'channel': 'C1', 'user': 'user1'}}
    dispatcher.handle_message(**msg_event)
    assert fake_plugin.listen_function.call_count == 1
    assert fake_plugin.respond_function.call_count == 0
    args = fake_plugin.listen_function.call_args
    _assert_message(args, 'hi')


def test_handle_event_respond_to(dispatcher, fake_plugin):
    msg_event = {'data': {'type': 'message', 'text': '<@123> hello', 'channel': 'C1', 'user': 'user1'}}
    dispatcher.handle_message(**msg_event)
    assert fake_plugin.respond_function.call_count == 1
    assert fake_plugin.listen_function.call_count == 0
    args = fake_plugin.respond_function.call_args
    _assert_message(args, 'hello')


def test_check_bot_mention(dispatcher):

    normal_msg_event = {'text': 'hi', 'channel': 'C1'}
    event = dispatcher._check_bot_mention(normal_msg_event)
    assert event is None

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
    assert event is None

    mention_msg_event_dm = {'text': 'hi', 'channel': 'D1'}
    event = dispatcher._check_bot_mention(mention_msg_event_dm)
    assert event == {'text': 'hi', 'channel': 'D1'}


def test_check_bot_mention_alias(dispatcher):

    mention_msg_event_no_alias_1 = {'text': '!hi', 'channel': 'C1'}
    event = dispatcher._check_bot_mention(mention_msg_event_no_alias_1)
    if dispatcher._aliases and '!' in dispatcher._aliases['ALIASES']:
        assert event == {'text': 'hi', 'channel': 'C1'}
    else:
        assert event is None

    mention_msg_event_no_alias_2 = {'text': '$hi', 'channel': 'C1'}
    event = dispatcher._check_bot_mention(mention_msg_event_no_alias_2)
    if dispatcher._aliases and '$' in dispatcher._aliases['ALIASES']:
        assert event == {'text': 'hi', 'channel': 'C1'}
    elif dispatcher._aliases and '!' in dispatcher._aliases['ALIASES']:
        assert event is None
    else:
        assert event is None
