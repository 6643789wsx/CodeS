import logging
import sys
import time

from .codes import *

logger = logging.getLogger(__name__)

if sys.version[0] < "3":
    string_types = (str, unicode)
else:
    string_types = (str,)


class OBDResponse:
    """Standard response object for any OBDCommand"""

    def __init__(self, command=None, messages=None):
        self.command = command
        self.messages = messages if messages else []
        self.value = None
        self.time = time.time()

    @property
    def unit(self):
        # for backwards compatibility
        from obd import Unit  # local import to avoid cyclic-dependency

        if isinstance(self.value, Unit.Quantity):
            return str(self.value.u)
        elif self.value is None:
            return None
        else:
            return str(type(self.value))

    def is_null(self):
        return (not self.messages) or (self.value == None)

    def __str__(self):
        return str(self.value)


"""
    Special value types used in OBDResponses
    instantiated in decoders.py
"""


class Status:
    def __init__(self):
        self.MIL = False
        self.DTC_count = 0
        self.ignition_type = ""

        # make sure each test is available by name
        # until real data comes it. This also prevents things from
        # breaking when the user looks up a standard test that's null.
        null_test = StatusTest()
        for name in BASE_TESTS + SPARK_TESTS + COMPRESSION_TESTS:
            if name:  # filter out None/reserved tests
                self.__dict__[name] = null_test


class StatusTest:
    def __init__(self, name="", available=False, complete=False):
        self.name = name
        self.available = available
        self.complete = complete

    def __str__(self):
        a = "Available" if self.available else "Unavailable"
        c = "Complete" if self.complete else "Incomplete"
        return "Test %s: %s, %s" % (self.name, a, c)


class Monitor:
    def __init__(self):
        self._tests = {}  # tid : MonitorTest

        # make the standard TIDs available as null monitor tests
        # until real data comes it. This also prevents things from
        # breaking when the user looks up a standard test that's null.
        null_test = MonitorTest()

        for tid in TEST_IDS:
            name = TEST_IDS[tid][0]
            self.__dict__[name] = null_test
            self._tests[tid] = null_test

    def add_test(self, test):
        self._tests[test.tid] = test
        if test.name is not None:
            self.__dict__[test.name] = test

    @property
    def tests(self):
        return [test for test in self._tests.values() if not test.is_null()]

    def __str__(self):
        if len(self.tests) > 0:
            return "\n".join([str(t) for t in self.tests])
        else:
            return "No tests to report"

    def __len__(self):
        return len(self.tests)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._tests.get(key, MonitorTest())
        elif isinstance(key, string_types):
            return self.__dict__.get(key, MonitorTest())
        else:
            logger.warning(
                "Monitor test results can only be retrieved by TID value or property name"
            )


class MonitorTest:
    def __init__(self):
        self.tid = None
        self.name = None
        self.desc = None
        self.value = None
        self.min = None
        self.max = None

    @property
    def passed(self):
        if not self.is_null():
            return (self.value >= self.min) and (self.value <= self.max)
        else:
            return False

    def is_null(self):
        return (
            self.tid is None
            or self.value is None
            or self.min is None
            or self.max is None
        )

    def __str__(self):
        return "%s : %s [%s]" % (
            self.desc,
            str(self.value),
            "PASSED" if self.passed else "FAILED",
        )
