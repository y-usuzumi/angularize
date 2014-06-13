import inspect
import ast
import re

def issubclassofany(type, l):
    return True in map(lambda base: issubclass(type, base), l)

def class_stringify(cls):
    if issubclass(cls, type):
        

class ASTTranslator:
    def __init__(self, code):
        self.code = code

    def __node_translate(self, node):
        t = type(node)
        translator_name = "__%s_translate" % \
                          class_stringify(t.mro()[-3]) # dirty work
        self.__dict__[translator_name](node)

## TODO: 敢不敢把这玩意放元类里？

    # 节点类别组分发器
    for group in [
            ast.mod, ast.stmt, ast.expr, ast.expr_context,
            ast.slice, ast.boolop, ast.operator, ast.unaryop,
            ast.compop, ast.comprehension, ast.excepthandler,
            ast.arguments, ast.keyword, ast.alias
    ]:
        exec(
'''
def __{0}_translate(self, node):
    t = type(node)
    translator_name = "__%s_translate" % \
                      class_stringify(t.mro()[-4]) # dirty work
    self.__dict__[translator_name](node)
''' % )

    def __mod_translate(self, node):
        t = type(node)
        

    def __stmt_translate(self, node):
        t = type(node)

    def __expr_translate(self, node):
        t = type(node)

    def __expr_context_translate(self, node):
        # do nothing
        pass

    def __slice_translate(self, node):
        # do nothing
        pass

    def __boolop_translate(self, node):
        # do nothing
        pass

    def __operator_translate(self, node):
        # do nothing
        pass

    def __unaryop_translate(self, node):
        # do nothing
        pass

    def __cmpop_translate(self, node):
        # do nothing
        pass

    def __comprehension_translate(self, node):
        # do nothing
        pass

    def __excepthandler_translate(self, node):
        # do nothing
        pass
        
    def __arguments_translate(self, node):
        # do nothing
        pass

    def __arg_translate(self, node):
        # do nothing
        pass

    def __keyword_translate(self, node):
        # do nothing
        pass

    def __alias_translate(self, node):
        # do nothing
        pass

    def __withitem_translate(self, node):
        # do nothing
        pass


        

def node_translate(node):
    t = type(node)
    if issubclass(t, ast.FuntionDef):
        _templ = "function {0}({1}) {{ {2} }}"
        return _templ.format(t.name, node_translate(t.args), func_body_translate(body))
            

def func_body_translate(body):
    for node in body:
        s = node_translate(node)


class Env:
    def puts(self, s):
        frameinfo = inspect.getframeinfo(inspect.currentframe())
        print("%s.%s(%s)" % (self, frameinfo[2], s))

if __name__ == '__main__':
    env = Env()
    root = ast.parse(
'''
def abc(a, b):
  print("IN")
  return a + b
''')
    # for node in ast.walk(root):
    #     if isinstance(node, ast.FunctionDef):
    #         print("function %s(
