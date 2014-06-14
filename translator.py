# -*- coding: utf-8 -*-
################################
# Angularize
# @author: Savor d'Isavano
# @date:  2014-06-13
################################

import inspect
import ast
import re
from collections import defaultdict

def issubclassofany(type, l):
    '''测试一个类型是否是列表中任一类型的子类型或自身'''
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

class AstTranslator:
    '''Python到JavaScript代码翻译器'''
    
    __function_mappings = {
        'print': 'console.log'
    }

    def __init__(self, code):
        self.code = code
        self.__block_level = 0
        self.__scope_variables = defaultdict(list)
        self.__tree_stack = [None]

    def _node_translate(self, node, *args, **kwargs):
        parent = self.__tree_stack[-1]
        
        if not isinstance(node, list):
            node = [node]

        res = []
        for n in node:
            if isinstance(n, str) or isinstance(n, int):
                res.append(n)
                continue
                
            n.parent = parent
            self.__tree_stack.append(n)
            t = type(n)
            # dirty work
            translator_name = "_%s_translate" % \
                              class_stringify(t.mro()[-3])
            res.append(getattr(self, translator_name)(n, *args, **kwargs))
            self.__tree_stack.pop()
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
        self.__scope_variables[self.__block_level].append(node.arg)

        return node.arg

    def _arguments_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        res = []
        for arg in node.args:
            arg_res = _tmpl.format(
                self._node_translate(
                    arg, *args, **kwargs))
            res.append(arg_res)
            
        return ', '.join(res)


    def _Name_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        parent = node.parent
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
        targets = node.targets
        # TODO: Cannot do multiple assignments
        target = targets[0]
        name = self._node_translate(target)

        if isinstance(target, ast.Name) and \
           name not in self.__scope_variables[self.__block_level]:
            self.__scope_variables[self.__block_level].append(name)
            _tmpl = "var {0} = {1};"
        else:
            _tmpl = "{0} = {1};"
        return _tmpl.format(name, self._node_translate(node.value))

    def _Attribute_translate(self, node, *args, **kwargs):
        _tmpl = "{0}.{1}"
        return _tmpl.format(self._node_translate(node.value), self._node_translate(node.attr))

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
        return _tmpl.format(self._node_translate(node.func), args)
        

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

    def _Mult_translate(self, mode, *args, **kwargs):
        _tmpl = "{0}"
        return _tmpl.format("*")

    def _Div_translate(self, node, *args, **kwargs):
        _tmpl = "{0}"
        return _tmpl.format("/")

    def translate(self):
        '''执行翻译过程'''
        code = self.code
        if isinstance(self.code, str):
            code = ast.parse(self.code).body[0]
            
        return self._node_translate(code)


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
