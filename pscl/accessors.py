'''Descriptors that help access attributes from R types.
'''

class Accessor(object):
    '''A descriptor that behaves like a property, but converts an
    R type to a python equivalent before returning it.
    '''

    def __init__(self, key=None):
        '''Initialize an accessor. ``key`` can be passed in or defined
        on the instance.
        '''
        _key = getattr(self, 'key', None) or key
        if _key is None:
            _key = self.__class__.__name__.lower()
        self.key = _key

    def __get__(self, inst, type_=None):
        self.inst = inst
        return self.get_value()

    def get_raw(self):
        return self.inst[self.key]

    def get_value(self):
        value = self.get_raw()
        # Then do something with it.
        raise NotImplemented


class ValueAccessor(Accessor):
    '''An accessor that casts an R vector to a list and pops
    off the last item.
    '''
    def get_value(self):
        value = self.get_raw()
        return list(value).pop()


class VectorAccessor(Accessor):
    '''An accessor that casts an R vector to a tuple.
    '''
    def get_value(self):
        value = self.get_raw()
        return tuple(value)



