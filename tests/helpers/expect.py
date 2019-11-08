# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, List
from unittest.mock import (
    DEFAULT,
    _Call,
    MagicMock,
    MagicMixin,
    MagicProxy,
    Mock,
    _magics,
    call,
    patch as mock_patch,
)

import pytest

_NO_VALUE = object()


class Expectation(object):
    """ An expectation is a mapping of a set of call arguments
        to a series of return values and/or raisables.
    """

    def __init__(self, sig: _Call):
        self.sig = sig
        self._items = []
        self._always = _NO_VALUE

    def _set_always(self, value: Any) -> Expectation:

        self._items.clear()
        self._always = value
        return self

    def _append_item(self, value: Any) -> Expectation:

        self._items.append(value)
        return self

    def _next_item(self) -> Any:

        if self._always is not _NO_VALUE:
            return self._always

        try:
            return self._items.pop(0)
        except IndexError:
            return _NO_VALUE

    def has_unused_items(self) -> bool:
        """ If this expectation has calls that are unused, returns true.
            If this expectation has an always value set, returns false.
        """

        if self._always is not _NO_VALUE:
            return False

        if len(self._items) > 0:
            return True

        return False

    def matches(self, *args, **kw) -> bool:
        """ If a given set of args and keyword args matches
            the represented call signature, returns True
        """

        if self.sig == call(*args, **kw):
            return True

        return False

    def returns(self, value: Any, always: bool = False) -> Expectation:
        """ When the `ExpectMock` is called with the arguments
            given by `self.sig`, `value` is returned.

            If `always` is set to `True`, this `Expectation`'s
            items will be replaced by the given value and will
            never become exhausted.
        """

        if always:
            return self._set_always(value)

        return self._append_item(value)

    def raises(self, value: Any, always: bool = False) -> Expectation:
        """ When the `ExpectMock` is called with the arguments
            given by `self.sig`, `value` is raised.

            If `always` is set to `True`, this `Expectation`'s
            items will be replaced by the given value and will
            never become exhausted.
        """

        if always:
            return self._set_always(value)

        return self._append_item(value)


class ExpectMixin(object):
    def __init__(self, ignore_unused_calls: bool = False):
        self.__expectations = []
        self._ignore_unused_calls = ignore_unused_calls

    def expect(self, *args, **kw) -> Expectation:
        this_call = call(*args, **kw)
        expectation = Expectation(this_call)
        self.__expectations.append(expectation)
        return expectation

    def raise_for_unused_calls(self):
        if self._ignore_unused_calls:
            return

        for expectation in self.__expectations:
            if expectation.has_unused_items():
                raise UnusedCallsError(self, expectation)

    def _expect_side_effect(self, *args, **kw) -> Any:
        for ex in self.__expectations:
            if ex.matches(*args, **kw):
                item = ex._next_item()
                if isinstance(item, Exception):
                    raise item
                elif item is _NO_VALUE:
                    raise NoExpectationForCall(*args, **kw)
                else:
                    return item
        else:
            raise NoExpectationForCall(*args, **kw)


class ExpectMock(ExpectMixin, Mock):
    """ `ExpectMock` is an expectation-based mock builder, built on
        top of the stdlib `unittest.mock` framework.

        `ExpectMock` aims to provide a `mockito`-esque interface to
        expecting call arguments paired with returns and/or raises.

        ---

        With vanilla `unittest.mock`, you would have to use something
        like this example to map a call to a return value or exception,
        and expect that the call happens before teardown:

            def test_function(mocker):
                calls = {
                    call(expected, call, args): expectedReturn,
                    call(other, call, args): Exception("message"),
                }

                def dispatcher(*args, **kw):
                    sig = call(*args, **kw)
                    if sig in calls:
                        item = calls[sig]
                        if isinstance(sig, Exception):
                            raise item
                        return calls[sig]

                function = mocker.patch("some.module.function")
                function.side_effect = dispatcher

                # Assume `caller_of_function` calls the mocked function
                caller_of_function(my, arguments)

                [function.assert_has_call(sig) for sig in calls.keys()]

        ---

        With `ExpectMock`, the above exchange becomes far simpler:

            def test_function(expecter):
                function = expecter.mock("some.module.function")
                function.expect(expected, call, args).returns(expectedReturn)
                function.expect(other, call, args).raises(Exception("message"))

                # Assume `caller_of_function` calls the mocked function
                caller_of_function(my, arguments)
    """

    def __init__(self, *args, ignore_unused_calls: bool = False, **kw):
        """ Initialize an `ExpectMock`.
        """

        Mock.__init__(self, *args, **kw)
        ExpectMixin.__init__(self, ignore_unused_calls=ignore_unused_calls)

        self.side_effect = self._expect_side_effect


class ExpectMagicMock(ExpectMixin, MagicMock):
    """ `ExpectMagicMock` is an extension of `ExpectMock` that has the
        same properties as both `ExpectMock` and `MagicMock`, but will
        also return new `ExpectMagicMock`s for magics.
    """

    def __init__(self, *args, ignore_unused_calls: bool = False, **kw):
        """ Initialize an `ExpectMock`.
        """

        MagicMock.__init__(self, *args, **kw)
        ExpectMixin.__init__(self, ignore_unused_calls=ignore_unused_calls)

        self.side_effect = self._expect_side_effect


class NoExpectationForCall(Exception):
    def __init__(self, *args, **kw):
        super().__init__(self)
        this_call = call(*args, **kw)
        self.message = f"ExpectMock has no expectation for call: {this_call}"

    def __repr__(self):
        return self.message

    def __str__(self):
        return repr(self)


class UnusedCallsError(Exception):
    def __init__(self, mock: ExpectMixin, expectation: Expectation):
        super().__init__(self)
        unused_calls = map(
            lambda item: f"  {expectation.sig} -> {item}", expectation._items
        )
        self.message = f"Mock {repr(mock)} has unused calls:\n{''.join(unused_calls)}"

    def __repr__(self):
        return self.message

    def __str__(self):
        return repr(self)


def patch(
    target,
    new=DEFAULT,
    spec=None,
    create=False,
    spec_set=None,
    autospec=None,
    new_callable=None,
    **kwargs,
):
    if new_callable is not None:
        if new is not DEFAULT:
            raise ValueError("Cannot use 'new' and 'new_callable' together")
    else:
        if new is DEFAULT:
            new = ExpectMagicMock

    return mock_patch(
        target,
        new=new,
        spec=spec,
        create=create,
        spec_set=spec_set,
        autospec=autospec,
        new_callable=new_callable,
        **kwargs,
    )


class ExpectMockFixture(object):
    """ ExpectMockFixture provides a patching interface for test functions
        and collects all created patches to ensure they are unstubbed after
        the test has completed

        Based upon the `MockFixture` from the excellent `pytest-mock` plugin.
    """

    def __init__(self):
        self._patches = []
        self._mocks = []

    def reset_all(self):
        for m in self._mocks:
            m.reset_mock()

    def stop_all(self):
        for p in reversed(self._patches):
            p.stop()

        self._patches.clear()
        self._mocks.clear()

    def check_for_unused_mock_calls(self):
        for m in self._mocks:
            m.raise_for_unused_calls()

    def patch(self, target, *args, **kw) -> ExpectMagicMock:
        if "new_callable" not in kw:
            kw["new_callable"] = ExpectMagicMock

        p = patch(target, *args, **kw)
        self._patches.append(p)
        m = p.start()
        self._mocks.append(m)
        return m

    def mock(self, *args, **kw) -> ExpectMagicMock:
        m = ExpectMagicMock(*args, **kw)
        self._mocks.append(m)
        return m

    MagicMock = mock
    ExpectMagicMock = mock


@pytest.yield_fixture
def expect():
    fixture = ExpectMockFixture()
    yield fixture
    try:
        fixture.check_for_unused_mock_calls()
    finally:
        fixture.stop_all()
