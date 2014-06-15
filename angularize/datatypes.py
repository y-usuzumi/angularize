from functools import wraps

def debug(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        print("Args: %s" % args)
        print("KWArgs: %s" % kwargs)
        func(*args, **kwargs)

    return new_func

class DataTypeDescriptor:
    '''Base descriptor class for data fields.
    A data field should at least validate the input data type.
    '''

    __type__ = object

    def __init__(self, name=None):
        self.name = name
        self._watched_hooks = []


    def __get__(self, instance, type=None):
        global _wtfnxtlr
        _wtfnxtlr = self
        return instance.__dict__[self.name]

    # def __getattribute__(self, key):
    #     descriptor = super().__getattribute__(key)


    def __set__(self, instance, value):
        self.instance = instance
        name = self.name
        def raiseTypeError(expected, actual):
            raise TypeError("%s expected. Got %s" % (expected, actual))

            
        if self.__dict__ and '__type__' in self.__dict__:
            _t = self.__dict__['__type__']
        else:
            _t = type(self).__type__

        if not isinstance(value, _t):
            raiseTypeError(_t, type(value))

        oldvalue = instance.__dict__.get(name, None)
        newvalue = value
        if oldvalue != newvalue:
            instance.__dict__[name] = value
            for hook in self._watched_hooks:
                hook(newvalue, oldvalue)

    def __delete__(self, instance):
        del instance.__dict__[self.name]


class Integer(DataTypeDescriptor):
    '''An integer data field.'''
    
    __type__ = int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Now we have nothing to do with args


class Float(DataTypeDescriptor):
    '''A float data field.'''

    __type__ = float
        
        
class String(DataTypeDescriptor):
    '''A string data field.'''

    __type__ = str

class Foreign(DataTypeDescriptor):
    '''Complex type.'''

    def __init__(self, *, type):
        self.__type__ = type

class Computed(DataTypeDescriptor):
    '''计算字段'''

    def __init__(self, *, rule):
        raise NotImplementedError("尚未实现")

        if not callable(rule):
            raise TypeError("%s不是一个callable对象" % rule)

class Watched(DataTypeDescriptor):
    '''监视字段'''

    def __init__(self, type, *args, rule, **kwargs):
        if not issubclass(type, DataTypeDescriptor):
            raise ValueError("%s不是一个“数据类型描述类”" % type)

        self.__class__.__type__ = type.__type__

        if not isinstance(rule, str):
            raise TypeError("现在rule只接收字符串对象")

        # if not callable(rule):
        #     raise TypeError("%s不是一个callable对象" % rule)

        # spec = getfullargspec(rule)
        # args_num = len(spec.args)
        # if args_num < 3:
        #     raise ValueError("%s只有%d个位置参数，至少需要3个" % (rule, args_num))

        self.rule = rule

        super().__init__(self, *args, **kwargs)

