import sys

if sys.version_info.major < 3:
    import Queue as queue # flake8: noqa
else:
    import queue # flake8: noqa
