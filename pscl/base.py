from rpy2 import robjects


def _iterable_to_R_type(iterable, c=robjects.r('c')):
    '''Pass (and unpack) an iterable into R's `c` function.
    '''
    return c(*iterable)


class Field(object):
    '''A descriptor for defining declarative translation interfaces between
    python kwargs and their R equivalents.
    '''

    class NotSet(object):
        '''A singleton for identifying unused function arguments.
        '''

    _PYTHON_R_VALUES = (
        (None, robjects.NULL),
        )

    c = robjects.r('c')
    _PYTHON_R_TYPES = (
        (tuple, _iterable_to_R_type),
        (list, _iterable_to_R_type),
        )

    def __get__(self, inst, type_=None):
        self.inst = inst
        return self.r_value()

    def __set__(self, inst, value):
        self.inst = inst
        inst.kwargs[self.name] = value

    def __init__(self, name, **kwargs):
        self.name = name
        if 'default' in kwargs:
            self.default = kwargs['default']
    def __repr__(self):
        return 'Field(name=%s, value=%s)' % (self.name, self.value)

    def __iter__(self):
        '''Enables tuple(myfield) to return (fieldname, r_value())
        '''
        yield self.name
        yield self.r_value()

    @property
    def value(self):
        return self.inst.kwargs.get(self.name, self.NotSet)

    def r_value(self):
        '''Convert this field to it's R equivalent. If's not set and a default
        is supplied, return the default. Otherwise return the NotSet type.
        '''
        val = self.value

        # Return the default if one is defined.
        if val is self.NotSet and hasattr(self, 'default'):
            val = self.default

        # Return the value's R equivalent if one is defined.
        for python_val, r_val in self._PYTHON_R_VALUES:
            if val == python_val:
                return r_val

        # Cast the value to an R type if one is defined.
        for type_, func in self._PYTHON_R_TYPES:
            if type(val) is type_:
                return func(val)

        return val


class _Fields(dict):
    '''A iterator for the fields dictionary that skips unset fields.
    '''
    def __iter__(self, NotSet=Field.NotSet):
        for field in self.values():
            name, value = tuple(field)
            if value is NotSet:
                continue
            yield field


class _CallTranslatorMeta(type):

    def __new__(meta, name, bases, attrs):
        fields = {}
        for membername, member in attrs.items():
            if isinstance(member, Field):
                fields[membername] = member
        attrs.update(_fields=_Fields(fields))
        return type.__new__(meta, name, bases, attrs)


class Translator(object):
    '''An object that allows mappings between python and R types to
    be specified declaratively, and offers some shrink-wrapped methods
    to convert python kwargs into R equivalents, call the class-level
    `r_type` with those arguments, then wrap the whole mess with the
    class-level `wrapper` class.
    '''
    __metaclass__ = _CallTranslatorMeta

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
        values = tuple(self._fields)
        return dict(values)

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

        # Provide python-like access to object attributes.
        self.update(obj.iteritems())

    # Mute the horrific R repr method of rpy2.
    __repr__ = object.__repr__
