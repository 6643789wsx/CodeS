from os.path import basename, dirname

from maybe import T, register_filter


def filter_move(path_old, path_new):
    if dirname(path_old) == dirname(path_new):
        label = "rename"
        path_new = basename(path_new)
    else:
        label = "move"
    return (
        "%s %s to %s" % (T.green(label), T.underline(path_old), T.underline(path_new)),
        0,
    )


register_filter(
    "rename",
    lambda process, args: filter_move(
        process.full_path(args[0]), process.full_path(args[1])
    ),
)
register_filter(
    "renameat",
    lambda process, args: filter_move(
        process.full_path(args[1], args[0]), process.full_path(args[3], args[2])
    ),
)
register_filter(
    "renameat2",
    lambda process, args: filter_move(
        process.full_path(args[1], args[0]), process.full_path(args[3], args[2])
    ),
)
