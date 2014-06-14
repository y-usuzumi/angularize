import unittest
from angularize.model import *
from translator import AstTranslator

class TestModel(NgzModel):
    test_1 = Integer()
    test_2 = Float()
    test_3 = Watched(Integer, rule='test_3_watcher')

    def test_3_watcher(me, n, o):
        me.test_2 = n + n


class TestAngularizeModel(unittest.TestCase):
    '''测试Angularize模型'''
    
    def setUp(self):
        pass

    def test_model_generate_from_watched_fields(self):
        model = TestModel(test_1 = 5, test_2 = 0.0, test_3 = 4)
        klass = model.__class__
        watched_object = klass.__dict__['test_3']
        rule = getattr(klass, watched_object.rule)
        import ast, inspect
        code_lines = inspect.getsourcelines(rule)[0]
        if code_lines:
            indent_len = len(code_lines[0]) - len(code_lines[0].lstrip())
            code_lines = [c[indent_len:] for c in code_lines]

        code = ''.join(code_lines)
            
        t = AstTranslator(code)
        