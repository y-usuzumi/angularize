# -*- coding: utf-8 -*-
################################
# Angularize
# @author: Savor d'Isavano
# @date:  2014-06-13
################################

import inspect
import ast
from contextlib import contextmanager
from utils.lang import class_stringify

class AstTranslator:
    '''Python到JavaScript代码翻译器'''

    # Python函数和其等价的JavaScript表达
    __function_mappings = {
        'print': 'console.log'
    }

    def __init__(self, code):
        self.code = code
        self.__block_level = 0  # 代码块深度
        self.__scope_variables = [[]]  # 作用域变量
        self.__tree_stack = [None]  # AST节点层级

    @contextmanager
    def _enter_block(self):
        '''进入深层代码块'''
        self.__block_level += 1
        self.__scope_variables.append([])
        yield
        self.__scope_variables.pop()
        self.__block_level -= 1

    @contextmanager
    def _enter_node_stack(self, node):
        '''进入深层AST节点层级'''
        parent = self.__tree_stack[-1]
        node.parent = parent
        self.__tree_stack.append(node)
        yield
        self.__tree_stack.pop()

    @property
    def _varlist(self):
        '''当前作用域下的变量名称列表'''
        return self.__scope_variables[self.__block_level]

    def _node_translate(self, nodes, *args, **kwargs):
        '''递归地翻译节点到JavaScript代码'''
        
        if not isinstance(nodes, list):
            nodes = [nodes]

        # 翻译结果列表
        res = []
        for node in nodes:
            # 有时node是节点，有时根本只是简单类型对象
            if isinstance(node, str) or isinstance(node, int):
                res.append(node)
                continue

            # 如果是节点
            with self._enter_node_stack(node):
                t = type(node)
                # dirty work，获取基本节点类型对应的分发器名称
                translator_name = "_%s_translate" % \
                                  class_stringify(t.mro()[-3])

                # 翻译当前节点，置入结果集
                res.append(
                    getattr(
                        self, translator_name
                    )(node, *args, **kwargs))

        # 如果有多个结果，用空格联结
        return ' '.join(res)

## TODO: 敢不敢把这玩意放元类里？

    # 节点类别组分发器
    for group in [
            'mod', 'stmt', 'expr', 'expr_context',
            'slice', 'boolop', 'operator', 'unaryop',
            'compop', 'comprehension', 'excepthandler',
    ]:
        # 生成组分发器代码
        exec(
'''
def _{0}_translate(self, node, *args, **kwargs):
    t = type(node)
    # dirty work，获取具体节点名称对应的翻译器名称
    translator_name = "_%s_translate" % \
                       class_stringify(t.mro()[-4]) # dirty work

    # 翻译完成
    return getattr(self, translator_name)(node, *args, **kwargs)
'''.format(group))

    def _arg_translate(self, node, *args, **kwargs):
        '''翻译单个参数'''

        # 参数与函数体同作用域
        self._varlist.append(node.arg)

        # 参数名作为翻译结果
        return node.arg

    def _arguments_translate(self, node, *args, **kwargs):
        '''翻译参数列表'''
        
        _tmpl = "{0}"
        res = []
        for arg in node.args:
            arg_res = _tmpl.format(
                self._node_translate(
                    arg, *args, **kwargs))
            res.append(arg_res)
            
        return ', '.join(res)


    def _Name_translate(self, node, *args, **kwargs):
        '''翻译名称'''
        
        _tmpl = "{0}"
        parent = node.parent
        id = node.id

        # 如果名称来自函数调用，需要查找等价的JavaScript表达
        if isinstance(parent, ast.Call):
            id = self.__function_mappings.get(id, id)
            
        return _tmpl.format(id)

    def _Expr_translate(self, node, *args, **kwargs):
        '''翻译表达式'''
        
        _tmpl = "{0}"
        return _tmpl.format(self._node_translate(node.value))

    def _Num_translate(self, node, *args, **kwargs):
        '''翻译数值'''
        
        _tmpl = "{0}"
        return _tmpl.format(node.n)

    def _Assign_translate(self, node, *args, **kwargs):
        '''翻译赋值'''
        
        targets = node.targets
        # TODO: 暂不支持多重赋值
        target = targets[0]
        name = self._node_translate(target)

        # 只有名称节点可能需要使用var
        if isinstance(target, ast.Name) and \
           name not in self._varlist:
            self._varlist.append(name)
            _tmpl = "var {0} = {1};"
        else:
            _tmpl = "{0} = {1};"
            
        return _tmpl.format(name, self._node_translate(node.value))

    def _Attribute_translate(self, node, *args, **kwargs):
        '''翻译属性'''
        
        _tmpl = "{0}.{1}"
        return _tmpl.format(self._node_translate(node.value), self._node_translate(node.attr))

    def _FunctionDef_translate(self, node, *args, **kwargs):
        '''翻译函数定义'''
        
        with self._enter_block():  # 进入代码块
            _tmpl = "function {0}({1}) {{ {2} }}"
            res = _tmpl.format(node.name,
                               self._node_translate(node.args),
                               self._node_translate(node.body))
            
        return res

    def _Call_translate(self, node, *args, **kwargs):
        '''翻译函数调用'''
        
        _tmpl = "{0}({1});"
        args = ','.join([self._node_translate(n) for n in node.args])
        return _tmpl.format(self._node_translate(node.func), args)
        

    def _Return_translate(self, node, *args, **kwargs):
        '''翻译返回值'''
        
        _tmpl = "return {0};"
        if hasattr(node.value, 'n'):
            return _tmpl.format(node.value.n)
        else:
            return _tmpl.format(self._node_translate(node.value));

    def _BinOp_translate(self, node, *args, **kwargs):
        '''翻译二元运算'''

        # 整除运算
        if isinstance(node.op, ast.FloorDiv):
            _tmpl = "parseInt({0} / {1})"
            return _tmpl.format(self._node_translate(node.left), self._node_translate(node.right))
        else:
            _tmpl = "{0} {1} {2}"
            return _tmpl.format(self._node_translate(node.left), self._node_translate(node.op), self._node_translate(node.right))

    def _Add_translate(self, node, *args, **kwargs):
        '''翻译加法运算符'''
        _tmpl = "{0}"
        return _tmpl.format("+")

    def _Sub_translate(self, node, *args, **kwargs):
        '''翻译减法运算符'''
        
        _tmpl = "{0}"
        return _tmpl.format("-")

    def _Mult_translate(self, mode, *args, **kwargs):
        '''翻译乘法运算符'''
        _tmpl = "{0}"
        return _tmpl.format("*")

    def _Div_translate(self, node, *args, **kwargs):
        '''翻译除法运算符'''
        
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
