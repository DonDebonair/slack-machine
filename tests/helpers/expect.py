# -*- coding: utf-8 -*-

from __future__ import annotations

from functools import partial
from typing import Any, List
from unittest.mock import (
    DEFAULT,
    _Call,
    _all_sync_magics,
    _async_method_magics,
    AsyncMock,
    AsyncMockMixin,
    AsyncMagicMixin,
    CallableMixin,
    MagicMock,
    MagicMixin,
    MagicProxy,
    Mock,
    NonCallableMagicMock,
    NonCallableMock,
    _magics,
    call,
    patch as mock_patch,
)

import pytest
from loguru import logger

_NO_VALUE = object()


class Expectation(object):
    """ An expectation is a mapping of a set of call arguments
        to a series of return values and/or raisables.
    """

    def __init__(self, sig: _Call, log_expectations: bool = False):
        self.sig = sig
        self._items = []
        self._always = _NO_VALUE
        self._log_expectations = log_expectations

    def __repr__(self):
        return (
            f"<Expectation {self.sig} #items={len(self._items)} always={self._always}>"
        )

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

        # Compare arguments directly to check for wildcard spacers
        for sig_arg, called_arg in zip(self.sig.args, args):
            if sig_arg != ... and sig_arg != called_arg:
                return False

        for called_key, called_val in kw.items():
            # If the keyword given in the call isn't in sig kwargs, fail
            if called_key not in self.sig.kwargs:
                return False
            # Implicit: keyword given in call is in sig kwargs -- check value equality
            elif (sig_val := self.sig.kwargs[called_key]) != called_val:
                # If the values are not equal and the sig keyword value isn't `...`
                if sig_val != ...:
                    return False

        for sig_key, sig_val in self.sig.kwargs.items():
            # If the keyword in the sig isn't in called kwargs, fail
            if sig_key not in kw:
                return False
            # Implicit: keyword given in sig is in called kwargs -- check value equality
            elif (called_val := kw[sig_key]) != sig_val:
                # If the values are not equal and the sig keyword value isn't `...`
                if sig_val != ...:
                    return False

        return True

    def returns(self, value: Any, always: bool = False) -> Expectation:
        """ When the `ExpectMock` is called with the arguments
            given by `self.sig`, `value` is returned.

            If `always` is set to `True`, this `Expectation`'s
            items will be replaced by the given value and will
            never become exhausted.
        """

        if self._log_expectations:
            message = f"{self.sig}: returning `{value}`"
            if always:
                message += " ALWAYS"

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

        if self._log_expectations:
            message = f"{self.sig}: raising `{value}`"
            if always:
                message += " ALWAYS"

        if always:
            return self._set_always(value)

        return self._append_item(value)


class ExpectMixin(object):
    def __init__(
        self, ignore_unused_calls: bool = False, log_expectations: bool = False
    ):
        self.__expectations = []
        self._ignore_unused_calls = ignore_unused_calls
        self._log_expectations = log_expectations

    def _get_mock_name(self):
        return self._mock_name or str(self)

    def expect(self, *args, **kw) -> Expectation:
        this_call = call(*args, **kw)

        if self._log_expectations:
            logger.debug(f"adding new expectation: {self._get_mock_name()} {this_call}")

        expectation = Expectation(this_call, log_expectations=self._log_expectations)
        self.__expectations.append(expectation)
        return expectation

    def raise_for_unused_calls(self):
        if self._ignore_unused_calls:
            return

        for expectation in self.__expectations:
            if expectation.has_unused_items():
                raise UnusedCallsError(self._get_mock_name(), expectation)

    def _expect_side_effect(self, *args, **kw) -> Any:
        for ex in self.__expectations:
            if ex.matches(*args, **kw):
                item = ex._next_item()
                if isinstance(item, Exception):
                    if self._log_expectations:
                        logger.debug(
                            f"consuming raisable for expectation: {ex} -> {item}"
                        )

                    raise item
                elif item is _NO_VALUE:
                    raise NoExpectationForCall(self._get_mock_name(), *args, **kw)
                else:
                    if self._log_expectations:
                        logger.debug(
                            f"consuming returnable for expectation: {ex} -> {item}"
                        )

                    return item
        else:
            raise NoExpectationForCall(self._get_mock_name(), *args, **kw)


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

    def __init__(
        self,
        *args,
        ignore_unused_calls: bool = False,
        log_expectations: bool = False,
        **kw,
    ):
        """ Initialize an `ExpectMock`.
        """

        Mock.__init__(self, *args, **kw)
        ExpectMixin.__init__(
            self,
            ignore_unused_calls=ignore_unused_calls,
            log_expectations=log_expectations,
        )

        self.side_effect = self._expect_side_effect


class AsyncExpectMock(ExpectMixin, AsyncMock):
    """ Async version of ExpectMock
    """

    def __init__(
        self,
        *args,
        ignore_unused_calls: bool = False,
        log_expectations: bool = False,
        **kw,
    ):
        """ Initialize an `AsyncExpectMock`.
        """

        AsyncMock.__init__(self, *args, **kw)
        ExpectMixin.__init__(
            self,
            ignore_unused_calls=ignore_unused_calls,
            log_expectations=log_expectations,
        )

        self.side_effect = self._expect_side_effect

    def _get_child_mock(self, **kw):
        """ From Python 3.8 stdlib unittest.mock: https://github.com/python/cpython/blob/3.8/Lib/unittest/mock.py
            Modified to return the proper Expect* classes instead of
            stdlib mocks.
            ---
            Create the child mocks for attributes and return value.
            By default child mocks will be the same type as the parent.
            Subclasses of Mock may want to override this to customize the way
            child mocks are made.
            For non-callable mocks the callable variant will be used (rather than
            any custom subclass).
        """

        _new_name = kw.get("_new_name")
        if _new_name in self.__dict__["_spec_asyncs"]:
            return AsyncExpectMock(**kw)

        _type = type(self)
        if issubclass(_type, MagicMock) and _new_name in _async_method_magics:
            # Any asynchronous magic becomes an AsyncExpectMock
            klass = AsyncExpectMock
        elif issubclass(_type, AsyncMockMixin):
            if (
                _new_name in _all_sync_magics
                or self._mock_methods
                and _new_name in self._mock_methods
            ):
                # Any synchronous method on AsyncExpectMock becomes an ExpectMagicMock
                klass = ExpectMagicMock
            else:
                klass = AsyncExpectMock
        elif not issubclass(_type, CallableMixin):
            if issubclass(_type, NonCallableMagicMock):
                klass = ExpectMagicMock
            elif issubclass(_type, NonCallableMock):
                klass = ExpectMock
        else:
            klass = _type.__mro__[1]

        if self._mock_sealed:
            attribute = "." + kw["name"] if "name" in kw else "()"
            mock_name = self._extract_mock_name() + attribute
            raise AttributeError(mock_name)

        return klass(**kw)


class ExpectMagicMock(ExpectMixin, MagicMock):
    """ `ExpectMagicMock` is an extension of `ExpectMock` that has the
        same properties as both `ExpectMock` and `MagicMock`, but will
        also return new `ExpectMagicMock`s for magics.
    """

    def __init__(
        self,
        *args,
        ignore_unused_calls: bool = False,
        log_expectations: bool = False,
        **kw,
    ):
        """ Initialize an `ExpectMock`.
        """

        MagicMock.__init__(self, *args, **kw)
        ExpectMixin.__init__(
            self,
            ignore_unused_calls=ignore_unused_calls,
            log_expectations=log_expectations,
        )

        self.side_effect = self._expect_side_effect


class NoExpectationForCall(Exception):
    def __init__(self, spec, *args, **kw):
        super().__init__(self)
        this_call = call(*args, **kw)
        self.message = f"No expectation for `{spec}`: {this_call}"

    def __repr__(self):
        return self.message

    def __str__(self):
        return repr(self)


class UnusedCallsError(Exception):
    def __init__(self, mock_name: str, expectation: Expectation):
        super().__init__(self)
        unused_count = len(expectation._items)
        unused_calls = map(
            lambda item: f"  {expectation.sig} -> {item}\n", expectation._items
        )
        self.message = f"Mock {mock_name} has {unused_count} unused calls:\n{''.join(unused_calls)}"

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


def patch_async(
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
            new = AsyncExpectMock

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

    def __init__(self, log_patches: bool = False, log_expectations: bool = False):
        self._patches = []
        self._mocks = []
        self._log_patches = log_patches
        self._log_expectations = log_expectations

    def reset_all(self):
        for m in self._mocks:
            m.reset_mock()

    def log(self, patches: bool = False, expectations: bool = False):
        self._log_patches = patches
        self._log_expectations = expectations

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

        if self._log_patches:
            logger.debug(f"patching {target}: *args={args}, **kw={kw}")

        p = patch(target, *args, log_expectations=self._log_expectations, **kw)
        self._patches.append(p)
        m = p.start()
        self._mocks.append(m)
        return m

    def patch_async(self, target, *args, **kw) -> AsyncExpectMock:
        if "new_callable" not in kw:
            kw["new_callable"] = AsyncExpectMock

        if self._log_patches:
            logger.debug(f"patching async {target}: *args={args}, **kw={kw}")

        p = patch(target, *args, log_expectations=self._log_expectations, **kw)
        self._patches.append(p)
        m = p.start()
        self._mocks.append(m)
        return m

    def mock(self, *args, **kw) -> ExpectMagicMock:
        m = ExpectMagicMock(*args, **kw)
        self._mocks.append(m)
        return m

    def mock_async(self, *args, **kw) -> AsyncExpectMock:
        m = AsyncExpectMock(*args, **kw)
        self._mocks.append(m)
        return m

    MagicMock = mock
    ExpectMagicMock = mock
    ExpectMock = mock
    AsyncExpectMock = mock_async


@pytest.fixture
def expect():
    fixture = ExpectMockFixture()
    yield fixture
    try:
        fixture.check_for_unused_mock_calls()
    finally:
        fixture.stop_all()
