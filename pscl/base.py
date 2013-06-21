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
        if hasattr(self, 'inst'):
            return 'Field(name=%r, value=%r)' % (self.name, self.value)
        else:
            return 'Field(name=%r)' % self.name

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


class _TranslatorMeta(type):

    def __new__(meta, name, bases, attrs):

        # Aggregate the Fields on this translater.
        fields = {}
        for membername, member in attrs.items():
            if isinstance(member, Field):
                fields[membername] = member

        for field_name, r_name in attrs.pop('field_names', []):
            # If a list of field names is defined on the class,
            # add them as simple fields with no default args.
            fields[field_name] = Field(r_name)

        # Make sure all defined fields are top level attrs on the class.
        attrs.update(fields)

        # Make an iterable of fields available on the class.
        attrs.update(_fields=_Fields(fields))

        return type.__new__(meta, name, bases, attrs)


class Translator(object):
    '''An object that allows mappings between python and R types to
    be specified declaratively, and offers some shrink-wrapped methods
    to convert python kwargs into R equivalents, call the class-level
    `r_type` with those arguments, then wrap the whole mess with the
    class-level `wrapper` class.
    '''
    __metaclass__ = _TranslatorMeta

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

    def _get_eq_vals(self):
        for attr in self.eq_attrs:
            try:
                yield getattr(self, attr)
            except AttributeError:
                pass

    def __eq__(self, other):
        '''For some reason, 2 identical R datastructures don't compare is equal
        to each for me through rpy2. Necessary for unit tests to work.
        '''
        return tuple(self._get_eq_vals()) == tuple(other._get_eq_vals())


class SubWrapper(Wrapper):

    def __init__(self):
        pass

    def __get__(self, inst, type_=None):
        obj = self.obj = inst[self.key]
        self.update(obj.iteritems())
        return self
