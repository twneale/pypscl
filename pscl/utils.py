import os
import contextlib


class Cached(object):
    '''Computes attribute value and caches it in instance.

    Example:
        class MyClass(object):
            def myMethod(self):
                # ...
            myMethod = Cached(myMethod)
    Use "del inst.myMethod" to clear cache.
    http://code.activestate.com/recipes/276643/
    '''
    def __init__(self, method, name=None):
        self.method = method
        self.name = name or method.__name__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        result = self.method(inst)
        setattr(inst, self.name, result)
        return result


@contextlib.contextmanager
def cd(path):
    '''Creates the path if it doesn't exist'''
    old_dir = os.getcwd()
    try:
        os.makedirs(path)
    except OSError:
        pass
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)
