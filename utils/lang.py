import re

def issubclass_of_any(type, l):
    '''测试一个类型是否是列表中任一类型或其子类型'''
    return True in map(lambda base: issubclass(type, base), l)

def class_stringify(cls):
    '''获取一个类型的简单字符串表示
    比如：
    <class 'int'> -> int
    <class 'generator.AstTranslator'> -> AstTranslator
    '''
    
    if isinstance(cls, type):
        cls_regex = re.compile("<class '(\w+\.)*(?P<cls>\w+)'>")
        match = cls_regex.match(str(cls))
        if not match:
            raise TypeError("%s is probably not a type", cls)
        return match.group('cls')
    else:
        raise TypeError("%s is not a type", cls)

