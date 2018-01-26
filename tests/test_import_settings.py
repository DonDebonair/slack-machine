from unittest.mock import patch
from machine.settings import import_settings


def test_normal_import_settings():
    settings, found = import_settings('tests.local_test_settings')
    assert found == True
    assert 'PLUGINS' in settings
    assert settings['PLUGINS'] == ['machine.plugins.builtin.general.PingPongPlugin',
                                   'machine.plugins.builtin.general.HelloPlugin',
                                   'machine.plugins.builtin.help.HelpPlugin',
                                   'machine.plugins.builtin.fun.memes.MemePlugin']
    assert 'SLACK_API_TOKEN' in settings
    assert settings['SLACK_API_TOKEN'] == 'xoxo-abc123'
    assert 'MY_PLUGIN_SETTING' in settings
    assert settings['MY_PLUGIN_SETTING'] == 'foobar'
    assert '_THIS_SHOULD_NOT_REGISTER' not in settings


def test_import_settings_non_existing_module():
    settings, found = import_settings('tests.does_not_exist')
    assert found == False
    assert 'PLUGINS' in settings
    assert settings['PLUGINS'] == ['machine.plugins.builtin.general.PingPongPlugin',
                                   'machine.plugins.builtin.general.HelloPlugin',
                                   'machine.plugins.builtin.help.HelpPlugin',
                                   'machine.plugins.builtin.fun.memes.MemePlugin']


def test_env_import_settings():
    with patch.dict('os.environ', {
        'SM_SETTING_1': 'SETTING1',
        'XM_SETTING_2': 'SETTING2',
        'SM_SLACK_API_TOKEN': 'xoxo-somethingelse'
    }):
        settings, found = import_settings('tests.local_test_settings')
        assert found == True
        assert 'SETTING_1' in settings
        assert settings['SETTING_1'] == 'SETTING1'
        assert 'SETTING_2' not in settings
        assert 'SLACK_API_TOKEN' in settings
        assert settings['SLACK_API_TOKEN'] == 'xoxo-somethingelse'
