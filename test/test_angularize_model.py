import unittest
from angularize.model import *

class TestModel(NgzModel):
    test_1 = Integer()
    test_2 = Float()



    def test_3_watcher(obj, n, o):
        obj.test_2 = n + n

    test_3 = Watched(Integer, rule=test_3_watcher)

class TestAngularizeModel(unittest.TestCase):
    '''测试Angularize模型'''
    
    def setUp(self):
        pass

    def test_至少表解释错误吧(self):
        model = TestModel(test_1 = 5, test_2 = 0.0, test_3 = 4)
