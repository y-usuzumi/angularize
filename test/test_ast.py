import unittest

class TestAst(unittest.TestCase):
    def setUp(self):
        pass

    def test_issubclassofany(self):
        from generator import issubclassofany
        from collections import defaultdict
        self.assertTrue(issubclassofany(defaultdict, [dict, int, str]))
        self.assertFalse(issubclassofany(defaultdict, [int, str, float]))

    def test_class_stringify(self):
        from generator import class_stringify
        import ast
        self.assertEqual(class_stringify(ast.stmt), 'stmt')
        self.assertEqual(class_stringify(ast.Module), 'Module')
        self.assertEqual(class_stringify(int), 'int')

    def test_ast_translator_methods_created_properly(self):
        from generator import AstTranslator
        self.assertTrue('_stmt_translate' in AstTranslator.__dict__)
        translator = AstTranslator(None)
        self.assertTrue(getattr(translator, '_stmt_translate') is not None)
        
    def test_ast_mro(self):
        import ast
        lv1_type = ast.Assign.mro()[-3]
        self.assertTrue(lv1_type is ast.stmt)
                        
    def test_ast_translator_translate_functions(self):
        from generator import AstTranslator
        
        code = '''def func(a, b): print(a // b)'''
        translator = AstTranslator(code)
        print(translator.node_translate())
        
        code = '''def func(): x = 3; x = 4'''
        translator = AstTranslator(code)
        print(translator.node_translate())
