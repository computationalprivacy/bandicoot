""" Provides compatibility fixes for Jython
"""

__all__ = ['next']


class Throw(object): pass
throw = Throw() # easy sentinel hack


def next(iterator, default=throw):
    try:
        iternext = iterator.next.__call__
    except AttributeError:
        raise TypeError("%s object is not an iterator" % type(iterator).__name__)
    try:
        return iternext()
    except StopIteration:
        if default is throw:
            raise
        return default


# Backport of datetime.datetime.totalseconds()
def total_seconds(td):
    return float((td.microseconds +
                  (td.seconds + td.days * 24 * 3600) * 10**6)) / 10**6
