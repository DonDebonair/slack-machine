import inspect
import re

import pytest

from machine.plugins import ee
from machine.plugins.decorators import (
    ActionConfig,
    CommandConfig,
    MatcherConfig,
    action,
    command,
    listen_to,
    on,
    process,
    required_settings,
    respond_to,
    schedule,
)


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
    @respond_to(r"hello-respond", re.IGNORECASE, handle_message_changed=True)
    def f(msg):
        pass

    return f


@pytest.fixture(scope="module")
def command_f():
    @command("/test")
    async def f(cmd):
        pass

    return f


@pytest.fixture(scope="module")
def command_f_no_slash():
    @command("no-slash-test")
    async def f(cmd):
        pass

    return f


@pytest.fixture(scope="module")
def command_f_generator():
    @command("/test-generator")
    async def f(cmd):
        yield "hello"

    return f


@pytest.fixture(scope="module")
def schedule_f():
    @schedule(hour="*/2", minute=30)
    def f():
        pass

    return f


@pytest.fixture(scope="module")
def on_f():
    @on("test_event")
    def f(msg):
        pass

    return f


@pytest.fixture(scope="module")
def action_f():
    @action("action_1", "block_2")
    def f(action_paylaod):
        pass

    return f


@pytest.fixture(scope="module")
def action_f_regex():
    @action(re.compile(r"action_\d", re.IGNORECASE), re.compile(r"block\d", re.IGNORECASE))
    def f(action_paylaod):
        pass

    return f


@pytest.fixture(scope="module")
def action_f_no_action_or_block():
    @action(None, None)
    def f(action_paylaod):
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
    assert listen_to_f.metadata.plugin_actions.listen_to == [
        MatcherConfig(regex=re.compile(r"hello-listen", re.IGNORECASE), handle_changed_message=False)
    ]


def test_respond_to(respond_to_f):
    assert hasattr(respond_to_f, "metadata")
    assert hasattr(respond_to_f.metadata, "plugin_actions")
    assert hasattr(respond_to_f.metadata.plugin_actions, "respond_to")
    assert respond_to_f.metadata.plugin_actions.respond_to == [
        MatcherConfig(regex=re.compile(r"hello-respond", re.IGNORECASE), handle_changed_message=True)
    ]


def test_command(command_f):
    assert hasattr(command_f, "metadata")
    assert hasattr(command_f.metadata, "plugin_actions")
    assert hasattr(command_f.metadata.plugin_actions, "commands")
    assert command_f.metadata.plugin_actions.commands == [CommandConfig(command="/test")]


def test_command_no_slash(command_f_no_slash):
    assert hasattr(command_f_no_slash, "metadata")
    assert hasattr(command_f_no_slash.metadata, "plugin_actions")
    assert hasattr(command_f_no_slash.metadata.plugin_actions, "commands")
    assert command_f_no_slash.metadata.plugin_actions.commands == [CommandConfig(command="/no-slash-test")]


def test_command_generator(command_f_generator):
    assert hasattr(command_f_generator, "metadata")
    assert hasattr(command_f_generator.metadata, "plugin_actions")
    assert hasattr(command_f_generator.metadata.plugin_actions, "commands")
    assert command_f_generator.metadata.plugin_actions.commands == [
        CommandConfig(command="/test-generator", is_generator=True)
    ]


def test_schedule(schedule_f):
    assert hasattr(schedule_f, "metadata")
    assert hasattr(schedule_f.metadata, "plugin_actions")
    assert hasattr(schedule_f.metadata.plugin_actions, "schedule")
    assert schedule_f.metadata.plugin_actions.schedule is not None
    assert schedule_f.metadata.plugin_actions.schedule["hour"] == "*/2"
    assert schedule_f.metadata.plugin_actions.schedule["minute"] == 30


def test_mulitple_decorators(multi_decorator_f):
    assert hasattr(multi_decorator_f, "metadata")
    assert hasattr(multi_decorator_f.metadata, "plugin_actions")
    assert hasattr(multi_decorator_f.metadata.plugin_actions, "respond_to")
    assert hasattr(multi_decorator_f.metadata.plugin_actions, "listen_to")
    assert hasattr(multi_decorator_f.metadata.plugin_actions, "process")
    assert multi_decorator_f.metadata.plugin_actions.respond_to == [
        MatcherConfig(regex=re.compile(r"hello-respond", re.IGNORECASE), handle_changed_message=False)
    ]
    assert multi_decorator_f.metadata.plugin_actions.listen_to == [
        MatcherConfig(regex=re.compile(r"hello-listen", re.IGNORECASE), handle_changed_message=False)
    ]
    assert multi_decorator_f.metadata.plugin_actions.process == []


def test_on(on_f):
    assert ee.event_names() == {"test_event"}
    listeners = ee.listeners("test_event")
    assert len(listeners) == 1
    assert listeners[0] == on_f


def test_action(action_f):
    assert hasattr(action_f, "metadata")
    assert hasattr(action_f.metadata, "plugin_actions")
    assert hasattr(action_f.metadata.plugin_actions, "actions")
    assert action_f.metadata.plugin_actions.actions == [ActionConfig(action_id="action_1", block_id="block_2")]
    action_cfg = action_f.metadata.plugin_actions.actions[0]
    assert isinstance(action_cfg.action_id, str)
    assert isinstance(action_cfg.block_id, str)


def test_action_regex(action_f_regex):
    assert hasattr(action_f_regex, "metadata")
    assert hasattr(action_f_regex.metadata, "plugin_actions")
    assert hasattr(action_f_regex.metadata.plugin_actions, "actions")
    action_id_pattern = re.compile(r"action_\d", re.IGNORECASE)
    block_id_pattern = re.compile(r"block\d", re.IGNORECASE)
    assert action_f_regex.metadata.plugin_actions.actions == [
        ActionConfig(action_id=action_id_pattern, block_id=block_id_pattern)
    ]
    action_cfg = action_f_regex.metadata.plugin_actions.actions[0]
    assert isinstance(action_cfg.action_id, re.Pattern)
    assert isinstance(action_cfg.block_id, re.Pattern)


def test_action_no_action_or_block():
    with pytest.raises(ValueError, match="At least one of action_id or block_id must be provided"):

        @action(None, None)
        def f(action_paylaod):
            pass


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
