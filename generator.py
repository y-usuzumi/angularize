import inspect
import ast
import re
from collections import defaultdict

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
    __function_mappings = {
        'print': 'console.log'
    }

    def __init__(self, code):
        self.code = code
        self.__block_level = 0
        self.__scope_variables = defaultdict(list)

    def _node_translate(self, node, *args, **kwargs):
        if not isinstance(node, list):
            node = [node]
        res = []
        for n in node:
            t = type(n)
            # dirty work
            translator_name = "_%s_translate" % \
                              class_stringify(t.mro()[-3])
            res.append(getattr(self, translator_name)(n, *args, **kwargs))
        return ' '.join(res)

## TODO: 敢不敢把这玩意放元类里？

    # 节点类别组分发器
    for group in [
            'mod', 'stmt', 'expr', 'expr_context',
            'slice', 'boolop', 'operator', 'unaryop',
            'compop', 'comprehension', 'excepthandler',
    ]:
        exec(
'''
def _{0}_translate(self, node, *args, **kwargs):
    t = type(node)
    translator_name = "_%s_translate" % \
                       class_stringify(t.mro()[-4]) # dirty work
    return getattr(self, translator_name)(node, *args, **kwargs)
'''.format(group))

    def _arg_translate(self, node, *args, **kwargs):
        return node.arg

    def _arguments_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        return ', '.join([_tmpl.format(self._node_translate(arg)) for arg in node.args])

    def _Name_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        parent = kwargs.get('parent', None)
        id = node.id
        if isinstance(parent, ast.Call):
            # function transformation
            id = self.__function_mappings.get(id, id)
        return _tmpl.format(id)

    def _Expr_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        return _tmpl.format(self._node_translate(node.value))

    def _Num_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        return _tmpl.format(node.n)

    def _Assign_translate(self, node, *args, **kwargs):
        # TODO: Not checking global variables and stuff.
        names = [name.id for name in node.targets]
        # TODO: Cannot do multiple assignments
        name = names[0]
        if name not in self.__scope_variables[self.__block_level]:
            self.__scope_variables[self.__block_level].append(name)
            _tmpl = "var {0} = {1};"
        else:
            _tmpl = "{0} = {1};"
        return _tmpl.format(name, self._node_translate(node.value))

    def _FunctionDef_translate(self, node, *args, **kwargs):
        self.__block_level += 1
        _tmpl = "function {0}({1}) {{ {2} }}"
        res = _tmpl.format(node.name, self._node_translate(node.args), self._node_translate(node.body))
        self.__scope_variables[self.__block_level].clear()
        self.__block_level -= 1
        return res

    def _Call_translate(self, node, *args, **kwargs):
        _tmpl = "{0}({1});"
        args = ','.join([self._node_translate(n) for n in node.args])
        return _tmpl.format(self._node_translate(node.func, parent=node), args)
        

    def _Return_translate(self, node, *args, **kwargs):
        _tmpl = "return {0};"
        if hasattr(node.value, 'n'):
            return _tmpl.format(node.value.n)
        else:
            return _tmpl.format(self._node_translate(node.value));

    def _BinOp_translate(self, node, *args, **kwargs):
        if isinstance(node.op, ast.FloorDiv):
            _tmpl = "parseInt({0} / {1})"
            return _tmpl.format(self._node_translate(node.left), self._node_translate(node.right))
        else:
            _tmpl = "{0} {1} {2}"
            return _tmpl.format(self._node_translate(node.left), self._node_translate(node.op), self._node_translate(node.right))

    def _Add_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        return _tmpl.format("+")

    def _Sub_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        return _tmpl.format("-")

    def _Div_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        return _tmpl.format("/")

    def node_translate(self):
        code = self.code
        if isinstance(self.code, str):
            code = ast.parse(self.code).body[0]
            
        return self._node_translate(code)


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
