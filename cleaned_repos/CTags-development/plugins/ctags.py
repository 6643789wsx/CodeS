"""
A ctags wrapper, parser and sorter.
"""

import bisect
import mmap
import os
import re
import subprocess
from subprocess import check_output

TAGS_RE = re.compile(
    r"(?P<symbol>[^\t]+)\t"
    r"(?P<filename>[^\t]+)\t"
    r'(?P<ex_command>(/.+/|\?.+\?|\d+));"\t'
    r"(?P<type>[^\t\r\n]+)"
    r"(?:\t(?P<fields>.*))?"
)

# column indexes
SYMBOL = 0
FILENAME = 1

MATCHES_STARTWITH = "starts_with"

PATH_ORDER = [
    "function",
    "class",
    "struct",
]

PATH_IGNORE_FIELDS = ("file", "access", "signature", "language", "line", "inherits")

TAG_PATH_SPLITTERS = ("/", ".", "::", ":")

#
# Functions
#

# Helper functions


def splits(string, *splitters):
    """
    Split a string on a number of splitters.

    :param string: string to split
    :param splitters: characters to split string on

    :returns: ``string`` split on characters in ``string``"""
    if splitters:
        split = string.split(splitters[0])
        for val in split:
            for char in splits(val, *splitters[1:]):
                yield char
    else:
        if string:
            yield string


# Tag processing functions


def parse_tag_lines(lines, order_by="symbol", tag_class=None, filters=None):
    """
    Parse and sort a list of tags.

    Parse and sort a list of tags one by using a combination of regexen and
    Python functions. The end result is a dictionary containing all 'tags' or
    entries found in the list of tags, sorted and filtered in a manner
    specified by the user.

    :param lines: list of tag lines from a tagfile
    :param order_by: element by which the result should be sorted
    :param tag_class: a Class to wrap around the resulting dictionary
    :param filters: filters to apply to resulting dictionary

    :returns: tag object or dictionary containing a sorted, filtered version
        of the original input tag lines
    """
    tags_lookup = {}

    for line in lines:
        skip = False

        if isinstance(line, Tag):  # handle both text and tag objects
            line = line.line

        line = line.rstrip("\r\n")

        search_obj = TAGS_RE.search(line)

        if not search_obj:
            continue

        tag = search_obj.groupdict()  # convert regex search result to dict

        tag = post_process_tag(tag)

        if tag_class is not None:  # if 'casting' to a class
            tag = tag_class(tag)

        if filters:
            # apply filters, filtering out any matching entries
            for filt in filters:
                for key, val in list(filt.items()):
                    if re.match(val, tag[key]):
                        skip = True

        if skip:  # if a filter was matched, ignore line (filter out)
            continue

        tags_lookup.setdefault(tag[order_by], []).append(tag)

    return tags_lookup


def post_process_tag(tag):
    """
    Process 'EX Command'-related elements of a tag.

    Process all 'EX Command'-related elements. The 'Ex Command' element has
    previously been split into the 'fields', 'type' and 'ex_command' elements.
    Break these down further as seen below::

        =========== = ============= =========================================
        original    > new           meaning/example
        =========== = ============= =========================================
        symbol      > symbol        symbol name (i.e. class, variable)
        filename    > filename      file containing symbol
        .           > tag_path      tuple of (filename, [class], symbol)
        ex_command  > ex_command    line number or regex used to find symbol
        type        > type          type of symbol (i.e. class, method)
        fields      > fields        string of fields
        .           > [field_keys]  list of parsed field keys
        .           > [field_one]   parsed field element one
        .           > [...]         additional parsed field element
        =========== = ============= =========================================

    Example::

        =========== = ============= =========================================
        original    > new           example
        =========== = ============= =========================================
        symbol      > symbol        'getSum'
        filename    > filename      'DemoClass.java'
        .           > tag_path      ('DemoClass.java', 'DemoClass', 'getSum')
        ex_command  > ex_command    '\tprivate int getSum(int a, int b) {'
        type        > type          'm'
        fields      > fields        'class:DemoClass\tfile:'
        .           > field_keys    ['class', 'file']
        .           > class         'DemoClass'
        .           > file          ''
        =========== = ============= =========================================

    :param tag: dict containing the unprocessed tag

    :returns: dict containing the processed tag
    """
    tag.update(process_fields(tag))

    tag["ex_command"] = process_ex_cmd(tag)

    tag.update(create_tag_path(tag))

    return tag


def process_ex_cmd(tag):
    """
    Process the 'ex_command' element of a tag dictionary.

    Process the ex_command string - a line number or regex used to find symbol
    declaration - by unescaping the regex where used.

    :param tag: dict containing a tag

    :returns: updated 'ex_command' dictionary entry
    """
    ex_cmd = tag.get("ex_command")

    if ex_cmd.isdigit():  # if a line number, do nothing
        return ex_cmd
    else:  # else a regex, so unescape
        return re.sub(r"\\(\$|/|\^|\\)", r"\1", ex_cmd[2:-2])  # unescape regex


def process_fields(tag):
    """
    Process the 'field' element of a tag dictionary.

    Process the fields string - a comma-separated string of "key-value" pairs
    - by generating key-value pairs and appending them to the tag dictionary.
    Also append a list of keys for said pairs.

    :param tag: dict containing a tag

    :returns: dict containing the key-value pairs from the field element, plus
        a list of keys for said pairs
    """
    fields = tag.get("fields")

    if not fields:  # do nothing
        return {}

    # split the fields string into a dictionary of key-value pairs
    result = dict(f.split(":", 1) for f in fields.split("\t"))

    # append all keys to the dictionary
    result["field_keys"] = sorted(result.keys())

    return result


def create_tag_path(tag):
    """
    Create a tag path entry for a tag dictionary.

    Creates a tag path entry for a tag dictionary from the field key-value
    pairs. Uses format::

        [function] [class] [struct] [additional entries] symbol

    Where ``additional entries`` is any field key-value pair not found in
    ``PATH_IGNORE_FIELDS``

    :param tag: dict containing a tag

    :returns: dict containing the 'tag_path' entry
    """
    field_keys = tag.get("field_keys", [])[:]
    fields = []
    tag_path = ""

    # sort field arguments related to path order in correct order
    for field in PATH_ORDER:
        if field in field_keys:
            fields.append(field)
            field_keys.pop(field_keys.index(field))

    # append all remaining field arguments
    fields.extend(field_keys)

    # convert list of fields to dot-joined string, dropping any "ignore" fields
    for field in fields:
        if field not in PATH_IGNORE_FIELDS:
            tag_path += tag.get(field) + "."

    # append symbol as last item in string
    tag_path += tag.get("symbol")

    # split string on seperators and append tag filename to resulting list
    splitup = [tag.get("filename")] + list(splits(tag_path, *TAG_PATH_SPLITTERS))

    # convert list to tuple
    result = {"tag_path": tuple(splitup)}

    return result


# Tag building/sorting functions


def build_ctags(path, cmd=None, tag_file=None, recursive=False, opts=None):
    """
    Execute the ``ctags`` command using ``Popen``.

    :param path: path to file or directory (with all files) to generate
        ctags for.
    :param recursive: specify if search should be recursive in directory
        given by path. This overrides filename specified by ``path``
    :param tag_file: filename to use for the tag file. Defaults to ``tags``
    :param opts: list of additional options to pass to the ctags executable

    :returns: original ``tag_file`` filename
    """
    # build the CTags command
    if cmd:
        cmd = [cmd]
    else:
        cmd = ["ctags"]

    if not os.path.exists(path):
        raise IOError(
            "'path' is not at valid directory or file path, or " "is not accessible"
        )

    if os.path.isfile(path):
        cwd = os.path.dirname(path)
    else:
        cwd = path

    if tag_file:
        cmd.append("-f {0}".format(tag_file))

    if opts:
        if type(opts) == list:
            cmd.extend(opts)
        else:  # *should* be a list, but better safe than sorry
            cmd.append(opts)

    if recursive:  # ignore any file specified in path if recursive set
        cmd.append("-R")
    elif os.path.isfile(path):
        filename = os.path.basename(path)
        cmd.append(filename)
    else:  # search all files in current directory
        cmd.append(os.path.join(path, "*"))

    # workaround for the issue described here:
    #   http://bugs.python.org/issue6689
    if os.name == "posix":
        cmd = " ".join(cmd)

    # execute the command
    check_output(
        cmd, cwd=cwd, shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    if not tag_file:  # Exuberant ctags defaults to ``tags`` filename.
        tag_file = os.path.join(cwd, "tags")
    else:
        if os.path.dirname(tag_file) != cwd:
            tag_file = os.path.join(cwd, tag_file)

    # re-sort ctag file in filename order to improve search performance
    resort_ctags(tag_file)

    return tag_file


def resort_ctags(tag_file):
    """
    Rearrange ctags file for speed.

    Resorts (re-sort) a CTag file in order of file. This improves searching
    performance when searching tags by file as a binary search can be used.

    The algorithm works as so:

        For each line in the tag file
            Read the file name (``file_name``) the tag belongs to
            If not exists, create an empty array and store in the
                dictionary with the file name as key
            Save the line to this list
        Create a new ``tagfile`` file
        For each key in the sorted dictionary
            For each line in the list indicated by the key
                Split the line on tab character
                Remove the prepending ``.`` from the ``file_name`` part of
                    the                   tag
                Join the line again and write the ``sorted_by_file`` file

    :param tag_file: The location of the tagfile to be sorted

    :returns: None
    """
    groups = {}

    with open(tag_file, encoding="utf-8", errors="replace") as file_:
        for line in file_:
            # meta data not needed in sorted files
            if line.startswith("!_TAG"):
                continue

            # read all valid symbol tags, which contain at least
            # symbol name and containing file and build a list of tuples
            split = line.split("\t", FILENAME + 1)
            if len(split) > FILENAME:
                groups.setdefault(split[FILENAME], []).append(line)

    with open(
        tag_file + "_sorted_by_file", "w", encoding="utf-8", errors="replace"
    ) as file_:
        for group in sorted(groups):
            file_.writelines(groups[group])


#
# Models
#


class TagElements(dict):
    """
    Model the entries of a tag file.
    """

    def __init__(self, *args, **kw):
        """Initialise Tag object"""
        dict.__init__(self, *args, **kw)
        self.__dict__ = self


class Tag(object):
    """
    Model a tag.

    This exists mainly to enable different types of sorting.
    """

    def __init__(self, line, column=0):
        if isinstance(line, bytes):  # python 3 compatibility
            line = line.decode("utf-8", "replace")
        self.line = line
        self.column = column

    def __lt__(self, other):
        try:
            return self.key < other
        except IndexError:
            return False

    def __gt__(self, other):
        try:
            return self.key > other
        except IndexError:
            return False

    def __getitem__(self, index):
        return self.line.split("\t", self.column + 1)[index]

    def __len__(self):
        return self.line.count("\t") + 1

    @property
    def key(self):
        return self[self.column]


class TagFile(object):
    """
    Model a tag file.

    This doesn't actually hold a entire tag file, due in part to the sheer
    size of some tag files (> 100 MB files are possible). Instead, it acts
    as a 'wrapper' of sorts around a file, providing functionality like
    searching for a retrieving tags, finding tags based on given criteria
    (prefix, suffix, exact), getting the directory of a tag and so forth.
    """

    def __init__(self, path, column):
        """
        Initialise object.

        The file indicated by ``path`` must be sorted by values in the column
        indicated by ``column``.

        :param path: path to a tag file
        :param column: column to search on

        :returns: None
        """
        self.path = path
        self.column = column
        self.file = None
        self.mmap = None

    def __getitem__(self, index):
        """
        Provide sequence-type interface to tag file.
        """
        if not self.mmap:
            raise RuntimeError("No tag file open.")

        self.mmap.seek(index)
        result = self.mmap.readline()

        if index != 0:  # handle first line
            result = self.mmap.readline()  # get a complete line

        result = result.strip()
        if not result:
            raise IndexError("Invalid tag at index %d." % index)

        return Tag(result, self.column)

    def __len__(self):
        """
        Get size of tag file in bytes.
        """
        if not self.mmap:
            raise RuntimeError("No tag file open.")

        return len(self.mmap)

    def __enter__(self):
        """
        Open file on enter when using ``with`` keyword.
        """
        self.open()
        return self

    def __exit__(self, type_, value, traceback):
        """
        Close file on exit when using ``with`` keyword.
        """
        self.close()

    @property
    def dir(self):
        """
        Get directory of tag file.
        """
        return os.path.dirname(self.path)

    def open(self):
        """
        Open file.
        """
        self.file = open(self.path, "r", encoding="utf-8")
        self.mmap = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)

    def close(self):
        """
        Close file.
        """
        if not self.mmap or not self.file:
            raise RuntimeError("No tag file open.")

        self.mmap.close()
        self.mmap = None
        self.file.close()
        self.file = None

    def search(self, exact_match=True, *tags):
        """
        Search for one or more tags in the tag file.

        Search a tag file for given tags using a binary search.

        :param exact_match: if search should be an exact or partial match

        :returns: matching tags
        """
        if not self.mmap:
            raise RuntimeError("No tag file open.")

        if not tags:
            while self.mmap.tell() < self.mmap.size():
                result = Tag(self.mmap.readline().strip(), self.column)
                if result.line:
                    yield result
            return

        for key in tags:
            left_index = bisect.bisect_left(self, key)
            if exact_match:
                result = self[left_index]
                while result.line and result[result.column] == key:
                    yield result
                    result = Tag(self.mmap.readline().strip(), self.column)
            else:
                result = self[left_index]
                while result.line and result[result.column].startswith(key):
                    yield result
                    result = Tag(self.mmap.readline().strip(), self.column)

    def search_by_suffix(self, suffix):
        """
        Search for one or more tags with the given suffix in the tag file.

        Search a tag file for given tags with the given suffix, using a linear
        search. Note that this linear search requires the entire file be
        searched making it slow. Hence, it should be avoided if possible.

        :param suffix: suffix to search for

        :returns: matching tags
        """
        if not self.file:
            raise RuntimeError("No tag file open.")

        for line in self.file:
            tag = Tag(line, self.column)
            if tag.key.endswith(suffix):
                yield tag

    def tag_class(self):
        """
        Default class to wrap tag in.

        Allows wrapping of a parsed tag dict in a class, so elements can be
        accessed as class variables (i.e. ``class.variable``, rather than
        ``dict['variable'])
        """
        return type("TagElements", (TagElements,), dict(root_dir=self.dir))

    def get_tags_dict(self, *tags, **kw):
        """
        Return the tags from a tag file as a dict.
        """
        filters = kw.get("filters", [])
        return parse_tag_lines(
            self.search(True, *tags), tag_class=self.tag_class(), filters=filters
        )

    def get_tags_dict_by_suffix(self, suffix, **kw):
        """
        Return the tags with the given suffix of a tag file as a dict.
        """
        filters = kw.get("filters", [])
        return parse_tag_lines(
            self.search_by_suffix(suffix), tag_class=self.tag_class(), filters=filters
        )
