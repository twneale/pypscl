'''Descriptors that help access attributes from R types.
'''

class Accessor(object):
    '''A descriptor that behaves like a property, but converts an
    R type to a python equivalent before returning it.
    '''

    def __init__(self, key):
        self.key = key

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



