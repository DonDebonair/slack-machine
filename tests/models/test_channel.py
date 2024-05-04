import pytest

from machine.models.channel import Channel


@pytest.fixture
def channel_dict():
    return {
        "id": "C1",
        "created": 0,
        "is_archived": False,
        "is_org_shared": False,
    }


def test_identifier_without_name(channel_dict):
    channel = Channel.model_validate(channel_dict)
    assert channel.identifier == "C1"


def test_identifier_with_name(channel_dict):
    channel_dict_with_name = dict(name="channel-1", **channel_dict)
    channel = Channel.model_validate(channel_dict_with_name)
    assert channel.identifier == "channel-1"
