import unittest
from angularize.model import NgzModel
from angularize.datatypes import *
from angularize.translator import NgzTranslator

class TestModel(NgzModel):
    test_1 = Integer()
    test_2 = Float()
    test_3 = Watched(Integer, rule='test_3_watcher')
    test_4 = String()

    def test_3_watcher(me, n, o):
        me.test_2 = n + n

class TestNgzTranslator(unittest.TestCase):
    '''测试Ngz翻译器'''

    def setUp(self):
        self.test_model = TestModel(
            test_1 = 5,
            test_2 = 0.0,
            test_3 = 4,
            test_4 = 'Test'
        )

    def test_translate(self):
        t = NgzTranslator(self.test_model)
        ## TODO: 翻译结果检查
        t.translate()
        
