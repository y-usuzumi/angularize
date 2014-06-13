import unittest

class TestAST(unittest.TestCase):
    def setUp(self):
        pass

    def test_issubclassofany(self):
        from generator import issubclassofany
        from collections import defaultdict
        self.assertTrue(issubclassofany(defaultdict, [dict, int, str]))
        self.assertFalse(issubclassofany(defaultdict, [int, str, float]))

    def test_ast_mro(self):
        import ast
        lv1_type = ast.Assign.mro()[-3]
        self.assertTrue(lv1_type is ast.stmt)
                        
