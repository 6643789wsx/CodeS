"""Checks if the current terminal supports colors.

Also specifies the stream to write to. On Windows, this is a wrapped
stream.
"""

from __future__ import absolute_import

import codecs
import errno
import os
import struct
import sys

from .context import PY3

STREAM = sys.stderr
ENCODING = getattr(STREAM, "encoding", None) or "utf-8"
SHOULD_ENCODE = True
SUPPORTS_COLOR = False


def to_byte(val):
    unicode_type = str if PY3 else unicode
    if isinstance(val, unicode_type):
        try:
            return val.encode(ENCODING)
        except UnicodeEncodeError:
            if PY3:
                return codecs.escape_decode(val)[0]
            else:
                return val.encode("unicode-escape").decode("string-escape")

    return val


def to_unicode(val):
    if isinstance(val, bytes):
        try:
            return val.decode(ENCODING)
        except UnicodeDecodeError:
            return val.decode("unicode-escape")

    return val


def get_terminfo_file():
    term = os.getenv("TERM", None)

    if term is None:
        return None

    terminfo_dirs = [
        os.path.expanduser("~/.terminfo"),
        "/etc/terminfo",
        "/lib/terminfo",
        "/usr/share/terminfo",
        "/usr/lib/terminfo",
        "/usr/share/lib/terminfo",
        "/usr/local/lib/terminfo",
        "/usr/local/share/terminfo",
    ]

    subdirs = [("%0.2X" % ord(term[0])), term[0]]

    f = None
    for terminfo_dir in terminfo_dirs:
        for subdir in subdirs:
            terminfo_path = os.path.join(terminfo_dir, subdir, term)
            try:
                f = open(terminfo_path, "rb")
                break
            except IOError as e:
                if e.errno != errno.ENOENT:
                    raise

    return f


class ProxyBufferStreamWrapper(object):
    def __init__(self, wrapped):
        self.__wrapped = wrapped

    def __getattr__(self, name):
        return getattr(self.__wrapped, name)

    def write(self, text):
        data = to_byte(text)
        self.__wrapped.buffer.write(data)


if os.name == "nt":
    from colorama import AnsiToWin32
    from colorama import init as init_colorama

    init_colorama(wrap=False)

    stream = sys.stderr

    if PY3:
        stream = ProxyBufferStreamWrapper(stream)
        SHOULD_ENCODE = False

    STREAM = AnsiToWin32(stream).stream
    SUPPORTS_COLOR = True
else:
    if os.getenv("FORCE_COLOR", None) == "1":
        SUPPORTS_COLOR = True
    else:
        try:
            # May raises an error on some exotic environment like GAE, see #28
            is_tty = os.isatty(2)
        except OSError:
            is_tty = False

        if is_tty:
            f = get_terminfo_file()
            if f is not None:
                with f:
                    # f is a valid terminfo; seek and read!
                    magic_number = struct.unpack("<h", f.read(2))[0]

                    if magic_number == 0x11A:
                        # the opened terminfo file is valid.
                        offset = (
                            2 + 10
                        )  # magic number + size section (the next thing we read from)
                        offset += struct.unpack("<h", f.read(2))[
                            0
                        ]  # skip over names section
                        offset += struct.unpack("<h", f.read(2))[
                            0
                        ]  # skip over bool section
                        offset += offset % 2  # align to short boundary
                        offset += 13 * 2  # maxColors is the 13th numeric value

                        f.seek(offset)
                        max_colors = struct.unpack("<h", f.read(2))[0]

                        if max_colors >= 8:
                            SUPPORTS_COLOR = True
