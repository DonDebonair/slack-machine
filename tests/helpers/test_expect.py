# -*- coding: utf-8 -*-

import time
from unittest.mock import call

import pytest

from tests.helpers.expect import (
    ExpectMagicMock,
    ExpectMock,
    ExpectMockFixture,
    Expectation,
    NoExpectationForCall,
    UnusedCallsError,
    expect,
    patch,
)


def test_basic_expectation():
    mock = ExpectMock()
    mock.expect("a").returns(1).returns(2)
    mock.expect("b").returns(3).returns(4)
    mock.expect("c").raises(Exception("C")).returns(5)

    assert mock("a") == 1
    assert mock("a") == 2
    with pytest.raises(NoExpectationForCall):
        mock("a")

    assert mock("b") == 3
    assert mock("b") == 4
    with pytest.raises(NoExpectationForCall):
        mock("b")

    with pytest.raises(Exception):
        mock("c")
    assert mock("c") == 5
    with pytest.raises(NoExpectationForCall):
        mock("c")


def test_call_record():
    mock = ExpectMock()
    mock.expect("a").returns(1).returns(2)

    assert mock("a") == 1
    mock.assert_has_calls([call("a")])

    assert mock("a") == 2
    mock.assert_has_calls([call("a"), call("a")])


def test_magic_child_instance():
    mock = ExpectMagicMock()
    assert isinstance(mock.some_function, ExpectMagicMock)
    assert isinstance(mock.__len__, ExpectMagicMock)


def test_patch():
    with patch("time.sleep", new_callable=ExpectMock) as sleep:
        sleep.expect(1).returns(True)
        assert time.sleep(1) == True


def test_always():
    mock = ExpectMagicMock()
    mock.expect("a").returns(1, always=True)
    mock.expect("b").returns(2, always=False)
    assert mock("a") == 1
    assert mock("b") == 2
    assert mock("a") == 1
    with pytest.raises(NoExpectationForCall):
        mock("b")


def test_expect_fixture(expect: ExpectMockFixture):
    assert isinstance(expect, ExpectMockFixture)
    sleep = expect.patch("time.sleep")
    sleep.expect(1).returns(True)
    assert time.sleep(1) == True

    expect.stop_all()
    assert time.sleep(0.1) == None


@pytest.mark.xfail(raises=UnusedCallsError, strict=True)
def test_raises_for_unused_calls(expect: ExpectMockFixture):
    sleep = expect.patch("time.sleep")
    sleep.expect(0.5).returns(True)
    sleep.expect(1).returns(True)
    assert time.sleep(0.5)
    expect.check_for_unused_mock_calls()


def test_ignore_unused_calls(expect: ExpectMockFixture):
    sleep = expect.patch("time.sleep", ignore_unused_calls=True)
    sleep.expect(0.5).returns(True)
    sleep.expect(1).returns(True)
    assert time.sleep(0.5)
    expect.check_for_unused_mock_calls()
