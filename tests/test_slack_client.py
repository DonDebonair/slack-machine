import pytest

from machine.models.user import User, Profile
from machine.models.channel import Channel
from machine.clients.slack import id_for_channel, id_for_user


@pytest.fixture
def user(mocker):
    p = mocker.MagicMock(spec=Profile)
    return User(id='1', team_id='t1', name='john', deleted=False, profile=p, is_bot=False,
                is_stranger=False, updated=0, is_app_user=False)


@pytest.fixture
def channel(mocker):
    c = mocker.MagicMock(spec=Channel)
    c.id = 'c1'
    return c


def test_id_for_user(user):
    assert id_for_user(user) == '1'
    assert id_for_user('2') == '2'


def test_id_for_channel(channel):
    assert id_for_channel(channel) == 'c1'
    assert id_for_channel('c2') == 'c2'
