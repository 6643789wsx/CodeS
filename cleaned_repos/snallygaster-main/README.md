snallygaster
============

Finds file leaks and other security problems on HTTP servers.

what?
-----

snallygaster is a tool that looks for files accessible on web servers that shouldn't be
public and can pose a security risk.

Typical examples include publicly accessible git repositories, backup files potentially
containing passwords or database dumps. In addition, it contains a few checks for other
security vulnerabilities.