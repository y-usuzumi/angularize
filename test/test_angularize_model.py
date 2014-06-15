import unittest
from .test_utils import code_matches_rule
from angularize.model import *
from angularize.translator import AstTranslator

class TestModel(NgzModel):
    test_1 = Integer()
    test_2 = Float()
    test_3 = Watched(Integer, rule='test_3_watcher')
    test_4 = String()

    def test_3_watcher(me, n, o):
        me.test_2 = n + n


class TestAngularizeModel(unittest.TestCase):
    '''测试Angularize模型'''
    
    def setUp(self):
        self.test_model = TestModel(
            test_1 = 5,
            test_2 = 0.0,
            test_3 = 4,
            test_4 = 'Test'
        )
        pass

    def test_model_string_representation(self):
        model = self.test_model
        model_repr = str(model)
        self.assertTrue("'test_1': 5" in model_repr)
        self.assertTrue("'test_2': 0.0" in model_repr)
        self.assertTrue("'test_3': 4" in model_repr)
        self.assertTrue("'test_4': 'Test'" in model_repr)
        

    def test_generate_code_from_model_watched_fields(self):
        model = self.test_model
        
        klass = model.__class__
        watched_object = klass.__dict__['test_3']
            
        t = AstTranslator(watched_object._code)
        
        
