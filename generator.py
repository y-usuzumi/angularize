import inspect
import ast
import re

def issubclassofany(type, l):
    return True in map(lambda base: issubclass(type, base), l)

def class_stringify(cls):
    if isinstance(cls, type):
        cls_regex = re.compile("<class '(\w+\.)*(?P<cls>\w+)'>")
        match = cls_regex.match(str(cls))
        if not match:
            raise TypeError("%s is probably not a type", cls)
        return match.group('cls')
    else:
        raise TypeError("%s is not a type", cls)

class AstTranslator:
    def __init__(self, code):
        self.code = code

    def _node_translate(self, node):
        t = type(node)
        if issubclass(t, list):
            node = node[0]
            t = type(node)
        translator_name = "_%s_translate" % \
                           class_stringify(t.mro()[-3]) # dirty work
        return getattr(self, translator_name)(node)

## TODO: 敢不敢把这玩意放元类里？

    # 节点类别组分发器
    for group in [
            'mod', 'stmt', 'expr', 'expr_context',
            'slice', 'boolop', 'operator', 'unaryop',
            'compop', 'comprehension', 'excepthandler',
    ]:
        exec(
'''
def _{0}_translate(self, node):
    t = type(node)
    translator_name = "_%s_translate" % \
                       class_stringify(t.mro()[-4]) # dirty work

    return getattr(self, translator_name)(node)
'''.format(group))

    def _arg_translate(self, node):
        return node.arg

    def _arguments_translate(self, node):
        _templ = "{0}"
        return ', '.join([_templ.format(self._node_translate(arg)) for arg in node.args])

    def _FunctionDef_translate(self, node):
        _templ = "function {0}({1}) {{ {2} }}"
        return _templ.format(node.name, self._node_translate(node.args), self._node_translate(node.body))

    def _Return_translate(self, node):
        _templ = "return {0};"
        if hasattr(node.value, 'n'):
            return _templ.format(node.value.n)
        else:
            return _templ.format(self._node_translate(node.value));

    def _BinOp_translate(self, node):
        _templ = "{0} {1} {2}"
        return _templ.format(self._node_translate(node.left), self._node_translate(node.op), self._node_translate(node.right))

    def _Name_translate(self, node):
        _templ = "{0}"
        return _templ.format(node.id)

    def _Add_translate(self, node):
        _templ = "{0}"
        return _templ.format("+")

    def node_translate(self, node):
        if isinstance(node, str):
            node = ast.parse(node).body[0]
            
        return self._node_translate(node)
            

def func_body_translate(body):
    return "TODO"
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
