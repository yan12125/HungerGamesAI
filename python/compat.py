import sys

PY3K = True

if sys.version_info.major < 3:
    PY3K = False
    import Queue as queue # flake8: noqa
else:
    import queue # flake8: noqa

def patch_range():
    global range
    if not PY3K:
        range = xrange

def patch_all():
    patch_range()
