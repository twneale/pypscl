import inspect

from rpy2.robjects import NULL


class Field(object):

    _PYTHON_R_VALUES = {
        None: NULL,
        }

    def __init__(self, name, default):
        self.name = name
        self.default = default

    def __get__(self, inst, type_=None):
        self.inst = inst
        return self.r_value()

    def __set__(self, inst, value):
        self.inst = inst
        inst.kwargs[self.name] = value

    def __repr__(self):
        return 'Field(name=%s, value=%s)' % (self.name, self.value)

    @property
    def value(self):
        return self.inst.kwargs.get(self.name, self.default)

    def r_value(self):
        '''Convert this field to it's R value.
        '''
        r_equiv = self._PYTHON_R_VALUES
        val = self.inst.kwargs.get(self.name, self.default)
        if val in r_equiv:
            return r_equiv[val]
        return val

    def __iter__(self):
        '''Enables tuple(myfield) to return (fieldname, r_value())
        '''
        yield self.name
        yield self.r_value()


class _BuilderMeta(type):

    def __new__(meta, name, bases, attrs):
        fields = {}
        for membername, member in attrs.items():
            if isinstance(member, Field):
                fields[membername] = member
        attrs.update(_fields=fields)
        return type.__new__(meta, name, bases, attrs)


class Builder(object):
    '''
    '''
    __metaclass__ = _BuilderMeta

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for fieldname, field in self._fields.items():
            if fieldname in kwargs:
                setattr(self, fieldname, kwargs[fieldname])
            else:
                # Seed the descriptors.
                getattr(self, fieldname)

    def r_kwargs(self):
        '''Convert the class's attributes to R arguments.
        '''
        return dict(map(tuple, self._fields.values()))

    def r_object(self, *args, **kwargs):
        r_kwargs = self.r_kwargs()
        r_kwargs.update(kwargs)
        r_object = self.r_type(*args, **r_kwargs)
        if hasattr(self, 'wrapper'):
            r_object = self.wrapper(r_object)
        return r_object


class Wrapper(dict):

    def __init__(self, obj):
        self.obj = obj

        # Provite python-like access to object attributes.
        self.update(obj.iteritems())



if __name__ == '__main__':
    x = Rollcall(yea=3, nay=4)
    print x.r_kwargs()
    import pdb; pdb.set_trace()
