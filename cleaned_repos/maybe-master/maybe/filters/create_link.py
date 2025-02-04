from maybe import T, register_filter


def filter_create_link(path_source, path_target, symbolic):
    label = "create symbolic link" if symbolic else "create hard link"
    return (
        "%s from %s to %s"
        % (T.cyan(label), T.underline(path_source), T.underline(path_target)),
        0,
    )


register_filter(
    "link",
    lambda process, args: filter_create_link(
        process.full_path(args[1]), process.full_path(args[0]), False
    ),
)
register_filter(
    "linkat",
    lambda process, args: filter_create_link(
        process.full_path(args[3], args[2]), process.full_path(args[1], args[0]), False
    ),
)
register_filter(
    "symlink",
    lambda process, args: filter_create_link(
        process.full_path(args[1]), process.full_path(args[0]), True
    ),
)
register_filter(
    "symlinkat",
    lambda process, args: filter_create_link(
        process.full_path(args[2], args[1]), process.full_path(args[0]), True
    ),
)
