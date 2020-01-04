import pytest

from machine.models.user import User, Profile


@pytest.fixture
def user(mocker):
    p = mocker.MagicMock(spec=Profile)
    return User(id='1', team_id='t1', name='john', deleted=False, profile=p, is_bot=False,
                is_stranger=False, updated=0, is_app_user=False)


def test_fmt_mention(user):
    expected = '<@1>'
    result = user.fmt_mention()
    assert result == expected
