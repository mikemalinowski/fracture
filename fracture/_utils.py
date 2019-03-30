"""
Holds small utility functions and classes
"""


# ------------------------------------------------------------------------------
class Signal(object):
    """
    A simple signal emmisison mechanism to allow for events within functions
    to trigger mid-call callbacks.
    """

    # --------------------------------------------------------------------------
    def __init__(self):
        self._callables = list()

    # --------------------------------------------------------------------------
    def connect(self, item):
        self._callables.append(item)

    # --------------------------------------------------------------------------
    def emit(self, *args, **kwargs):
        for item in self._callables:
            item(*args, **kwargs)
