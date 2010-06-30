import parser
import os
import unittest
import sys
import operator
from test import support

#
#  First, we test that we can generate trees from valid source fragments,
#  and that these valid trees are indeed allowed by the tree-loading side
#  of the parser module.
#

class RoundtripLegalSyntaxTestCase(unittest.TestCase):

    def roundtrip(self, f, s):
        st1 = f(s)
        t = st1.totuple()
        try:
            st2 = parser.sequence2st(t)
        except parser.ParserError as why:
            self.fail("could not roundtrip %r: %s" % (s, why))

        self.assertEquals(t, st2.totuple(),
                          "could not re-generate syntax tree")

    def check_expr(self, s):
        self.roundtrip(parser.expr, s)

    def test_flags_passed(self):
        # The unicode literals flags has to be passed from the paser to AST
        # generation.
        suite = parser.suite("from __future__ import unicode_literals; x = ''")
        code = suite.compile()
        scope = {}
        exec(code, {}, scope)
        self.assertTrue(isinstance(scope["x"], str))

    def check_suite(self, s):
        self.roundtrip(parser.suite, s)

    def test_yield_statement(self):
        self.check_suite("def f(): yield 1")
        self.check_suite("def f(): yield")
        self.check_suite("def f(): x += yield")
        self.check_suite("def f(): x = yield 1")
        self.check_suite("def f(): x = y = yield 1")
        self.check_suite("def f(): x = yield")
        self.check_suite("def f(): x = y = yield")
        self.check_suite("def f(): 1 + (yield)*2")
        self.check_suite("def f(): (yield 1)*2")
        self.check_suite("def f(): return; yield 1")
        self.check_suite("def f(): yield 1; return")
        self.check_suite("def f():\n"
                         "    for x in range(30):\n"
                         "        yield x\n")
        self.check_suite("def f():\n"
                         "    if (yield):\n"
                         "        yield x\n")

    def test_expressions(self):
        self.check_expr("foo(1)")
        self.check_expr("[1, 2, 3]")
        self.check_expr("[x**3 for x in range(20)]")
        self.check_expr("[x**3 for x in range(20) if x % 3]")
        self.check_expr("[x**3 for x in range(20) if x % 2 if x % 3]")
        self.check_expr("list(x**3 for x in range(20))")
        self.check_expr("list(x**3 for x in range(20) if x % 3)")
        self.check_expr("list(x**3 for x in range(20) if x % 2 if x % 3)")
        self.check_expr("foo(*args)")
        self.check_expr("foo(*args, **kw)")
        self.check_expr("foo(**kw)")
        self.check_expr("foo(key=value)")
        self.check_expr("foo(key=value, *args)")
        self.check_expr("foo(key=value, *args, **kw)")
        self.check_expr("foo(key=value, **kw)")
        self.check_expr("foo(a, b, c, *args)")
        self.check_expr("foo(a, b, c, *args, **kw)")
        self.check_expr("foo(a, b, c, **kw)")
        self.check_expr("foo(a, *args, keyword=23)")
        self.check_expr("foo + bar")
        self.check_expr("foo - bar")
        self.check_expr("foo * bar")
        self.check_expr("foo / bar")
        self.check_expr("foo // bar")
        self.check_expr("lambda: 0")
        self.check_expr("lambda x: 0")
        self.check_expr("lambda *y: 0")
        self.check_expr("lambda *y, **z: 0")
        self.check_expr("lambda **z: 0")
        self.check_expr("lambda x, y: 0")
        self.check_expr("lambda foo=bar: 0")
        self.check_expr("lambda foo=bar, spaz=nifty+spit: 0")
        self.check_expr("lambda foo=bar, **z: 0")
        self.check_expr("lambda foo=bar, blaz=blat+2, **z: 0")
        self.check_expr("lambda foo=bar, blaz=blat+2, *y, **z: 0")
        self.check_expr("lambda x, *y, **z: 0")
        self.check_expr("(x for x in range(10))")
        self.check_expr("foo(x for x in range(10))")

    def test_simple_expression(self):
        # expr_stmt
        self.check_suite("a")

    def test_simple_assignments(self):
        self.check_suite("a = b")
        self.check_suite("a = b = c = d = e")

    def test_simple_augmented_assignments(self):
        self.check_suite("a += b")
        self.check_suite("a -= b")
        self.check_suite("a *= b")
        self.check_suite("a /= b")
        self.check_suite("a //= b")
        self.check_suite("a %= b")
        self.check_suite("a &= b")
        self.check_suite("a |= b")
        self.check_suite("a ^= b")
        self.check_suite("a <<= b")
        self.check_suite("a >>= b")
        self.check_suite("a **= b")

    def test_function_defs(self):
        self.check_suite("def f(): pass")
        self.check_suite("def f(*args): pass")
        self.check_suite("def f(*args, **kw): pass")
        self.check_suite("def f(**kw): pass")
        self.check_suite("def f(foo=bar): pass")
        self.check_suite("def f(foo=bar, *args): pass")
        self.check_suite("def f(foo=bar, *args, **kw): pass")
        self.check_suite("def f(foo=bar, **kw): pass")

        self.check_suite("def f(a, b): pass")
        self.check_suite("def f(a, b, *args): pass")
        self.check_suite("def f(a, b, *args, **kw): pass")
        self.check_suite("def f(a, b, **kw): pass")
        self.check_suite("def f(a, b, foo=bar): pass")
        self.check_suite("def f(a, b, foo=bar, *args): pass")
        self.check_suite("def f(a, b, foo=bar, *args, **kw): pass")
        self.check_suite("def f(a, b, foo=bar, **kw): pass")

        self.check_suite("@staticmethod\n"
                         "def f(): pass")
        self.check_suite("@staticmethod\n"
                         "@funcattrs(x, y)\n"
                         "def f(): pass")
        self.check_suite("@funcattrs()\n"
                         "def f(): pass")

    def test_class_defs(self):
        self.check_suite("class foo():pass")
        self.check_suite("class foo(object):pass")

    def test_import_from_statement(self):
        self.check_suite("from sys.path import *")
        self.check_suite("from sys.path import dirname")
        self.check_suite("from sys.path import (dirname)")
        self.check_suite("from sys.path import (dirname,)")
        self.check_suite("from sys.path import dirname as my_dirname")
        self.check_suite("from sys.path import (dirname as my_dirname)")
        self.check_suite("from sys.path import (dirname as my_dirname,)")
        self.check_suite("from sys.path import dirname, basename")
        self.check_suite("from sys.path import (dirname, basename)")
        self.check_suite("from sys.path import (dirname, basename,)")
        self.check_suite(
            "from sys.path import dirname as my_dirname, basename")
        self.check_suite(
            "from sys.path import (dirname as my_dirname, basename)")
        self.check_suite(
            "from sys.path import (dirname as my_dirname, basename,)")
        self.check_suite(
            "from sys.path import dirname, basename as my_basename")
        self.check_suite(
            "from sys.path import (dirname, basename as my_basename)")
        self.check_suite(
            "from sys.path import (dirname, basename as my_basename,)")
        self.check_suite("from .bogus import x")

    def test_basic_import_statement(self):
        self.check_suite("import sys")
        self.check_suite("import sys as system")
        self.check_suite("import sys, math")
        self.check_suite("import sys as system, math")
        self.check_suite("import sys, math as my_math")

    def test_pep263(self):
        self.check_suite("# -*- coding: iso-8859-1 -*-\n"
                         "pass\n")

    def test_assert(self):
        self.check_suite("assert alo < ahi and blo < bhi\n")

    def test_with(self):
        self.check_suite("with open('x'): pass\n")
        self.check_suite("with open('x') as f: pass\n")
        self.check_suite("with open('x') as f, open('y') as g: pass\n")

    def test_try_stmt(self):
        self.check_suite("try: pass\nexcept: pass\n")
        self.check_suite("try: pass\nfinally: pass\n")
        self.check_suite("try: pass\nexcept A: pass\nfinally: pass\n")
        self.check_suite("try: pass\nexcept A: pass\nexcept: pass\n"
                         "finally: pass\n")
        self.check_suite("try: pass\nexcept: pass\nelse: pass\n")
        self.check_suite("try: pass\nexcept: pass\nelse: pass\n"
                         "finally: pass\n")

    def test_position(self):
        # An absolutely minimal test of position information.  Better
        # tests would be a big project.
        code = "def f(x):\n    return x + 1\n"
        st1 = parser.suite(code)
        st2 = st1.totuple(line_info=1, col_info=1)

        def walk(tree):
            node_type = tree[0]
            next = tree[1]
            if isinstance(next, tuple):
                for elt in tree[1:]:
                    for x in walk(elt):
                        yield x
            else:
                yield tree

        terminals = list(walk(st2))
        self.assertEqual([
            (1, 'def', 1, 0),
            (1, 'f', 1, 4),
            (7, '(', 1, 5),
            (1, 'x', 1, 6),
            (8, ')', 1, 7),
            (11, ':', 1, 8),
            (4, '', 1, 9),
            (5, '', 2, -1),
            (1, 'return', 2, 4),
            (1, 'x', 2, 11),
            (14, '+', 2, 13),
            (2, '1', 2, 15),
            (4, '', 2, 16),
            (6, '', 2, -1),
            (4, '', 2, -1),
            (0, '', 2, -1)],
                         terminals)


#
#  Second, we take *invalid* trees and make sure we get ParserError
#  rejections for them.
#

class IllegalSyntaxTestCase(unittest.TestCase):

    def check_bad_tree(self, tree, label):
        try:
            parser.sequence2st(tree)
        except parser.ParserError:
            pass
        else:
            self.fail("did not detect invalid tree for %r" % label)

    def test_junk(self):
        # not even remotely valid:
        self.check_bad_tree((1, 2, 3), "<junk>")

    def test_illegal_yield_1(self):
        # Illegal yield statement: def f(): return 1; yield 1
        tree = \
        (257,
         (264,
          (285,
           (259,
            (1, 'def'),
            (1, 'f'),
            (260, (7, '('), (8, ')')),
            (11, ':'),
            (291,
             (4, ''),
             (5, ''),
             (264,
              (265,
               (266,
                (272,
                 (275,
                  (1, 'return'),
                  (313,
                   (292,
                    (293,
                     (294,
                      (295,
                       (297,
                        (298,
                         (299,
                          (300,
                           (301,
                            (302, (303, (304, (305, (2, '1')))))))))))))))))),
               (264,
                (265,
                 (266,
                  (272,
                   (276,
                    (1, 'yield'),
                    (313,
                     (292,
                      (293,
                       (294,
                        (295,
                         (297,
                          (298,
                           (299,
                            (300,
                             (301,
                              (302,
                               (303, (304, (305, (2, '1')))))))))))))))))),
                 (4, ''))),
               (6, ''))))),
           (4, ''),
           (0, ''))))
        self.check_bad_tree(tree, "def f():\n  return 1\n  yield 1")

    def test_illegal_yield_2(self):
        # Illegal return in generator: def f(): return 1; yield 1
        tree = \
        (257,
         (264,
          (265,
           (266,
            (278,
             (1, 'from'),
             (281, (1, '__future__')),
             (1, 'import'),
             (279, (1, 'generators')))),
           (4, ''))),
         (264,
          (285,
           (259,
            (1, 'def'),
            (1, 'f'),
            (260, (7, '('), (8, ')')),
            (11, ':'),
            (291,
             (4, ''),
             (5, ''),
             (264,
              (265,
               (266,
                (272,
                 (275,
                  (1, 'return'),
                  (313,
                   (292,
                    (293,
                     (294,
                      (295,
                       (297,
                        (298,
                         (299,
                          (300,
                           (301,
                            (302, (303, (304, (305, (2, '1')))))))))))))))))),
               (264,
                (265,
                 (266,
                  (272,
                   (276,
                    (1, 'yield'),
                    (313,
                     (292,
                      (293,
                       (294,
                        (295,
                         (297,
                          (298,
                           (299,
                            (300,
                             (301,
                              (302,
                               (303, (304, (305, (2, '1')))))))))))))))))),
                 (4, ''))),
               (6, ''))))),
           (4, ''),
           (0, ''))))
        self.check_bad_tree(tree, "def f():\n  return 1\n  yield 1")

    def test_a_comma_comma_c(self):
        # Illegal input: a,,c
        tree = \
        (258,
         (311,
          (290,
           (291,
            (292,
             (293,
              (295,
               (296,
                (297,
                 (298, (299, (300, (301, (302, (303, (1, 'a')))))))))))))),
          (12, ','),
          (12, ','),
          (290,
           (291,
            (292,
             (293,
              (295,
               (296,
                (297,
                 (298, (299, (300, (301, (302, (303, (1, 'c'))))))))))))))),
         (4, ''),
         (0, ''))
        self.check_bad_tree(tree, "a,,c")

    def test_illegal_operator(self):
        # Illegal input: a $= b
        tree = \
        (257,
         (264,
          (265,
           (266,
            (267,
             (312,
              (291,
               (292,
                (293,
                 (294,
                  (296,
                   (297,
                    (298,
                     (299,
                      (300, (301, (302, (303, (304, (1, 'a'))))))))))))))),
             (268, (37, '$=')),
             (312,
              (291,
               (292,
                (293,
                 (294,
                  (296,
                   (297,
                    (298,
                     (299,
                      (300, (301, (302, (303, (304, (1, 'b'))))))))))))))))),
           (4, ''))),
         (0, ''))
        self.check_bad_tree(tree, "a $= b")

    def test_malformed_global(self):
        #doesn't have global keyword in ast
        tree = (257,
                (264,
                 (265,
                  (266,
                   (282, (1, 'foo'))), (4, ''))),
                (4, ''),
                (0, ''))
        self.check_bad_tree(tree, "malformed global ast")


class CompileTestCase(unittest.TestCase):

    # These tests are very minimal. :-(

    def test_compile_expr(self):
        st = parser.expr('2 + 3')
        code = parser.compilest(st)
        self.assertEquals(eval(code), 5)

    def test_compile_suite(self):
        st = parser.suite('x = 2; y = x + 3')
        code = parser.compilest(st)
        globs = {}
        exec(code, globs)
        self.assertEquals(globs['y'], 5)

    def test_compile_error(self):
        st = parser.suite('1 = 3 + 4')
        self.assertRaises(SyntaxError, parser.compilest, st)

    def test_compile_badunicode(self):
        st = parser.suite('a = "\\U12345678"')
        self.assertRaises(SyntaxError, parser.compilest, st)
        st = parser.suite('a = "\\u1"')
        self.assertRaises(SyntaxError, parser.compilest, st)

class ParserStackLimitTestCase(unittest.TestCase):
    """try to push the parser to/over its limits.
    see http://bugs.python.org/issue1881 for a discussion
    """
    def _nested_expression(self, level):
        return "["*level+"]"*level

    def test_deeply_nested_list(self):
        # XXX used to be 99 levels in 2.x
        e = self._nested_expression(93)
        st = parser.expr(e)
        st.compile()

    def test_trigger_memory_error(self):
        e = self._nested_expression(100)
        print("Expecting 's_push: parser stack overflow' in next line",
              file=sys.stderr)
        self.assertRaises(MemoryError, parser.expr, e)

class STObjectTestCase(unittest.TestCase):
    """Test operations on ST objects themselves"""

    def test_comparisons(self):
        # ST objects should support order and equality comparisons
        st1 = parser.expr('2 + 3')
        st2 = parser.suite('x = 2; y = x + 3')
        st3 = parser.expr('list(x**3 for x in range(20))')
        st1_copy = parser.expr('2 + 3')
        st2_copy = parser.suite('x = 2; y = x + 3')
        st3_copy = parser.expr('list(x**3 for x in range(20))')

        # exercise fast path for object identity
        self.assertEquals(st1 == st1, True)
        self.assertEquals(st2 == st2, True)
        self.assertEquals(st3 == st3, True)
        # slow path equality
        self.assertEqual(st1, st1_copy)
        self.assertEqual(st2, st2_copy)
        self.assertEqual(st3, st3_copy)
        self.assertEquals(st1 == st2, False)
        self.assertEquals(st1 == st3, False)
        self.assertEquals(st2 == st3, False)
        self.assertEquals(st1 != st1, False)
        self.assertEquals(st2 != st2, False)
        self.assertEquals(st3 != st3, False)
        self.assertEquals(st1 != st1_copy, False)
        self.assertEquals(st2 != st2_copy, False)
        self.assertEquals(st3 != st3_copy, False)
        self.assertEquals(st2 != st1, True)
        self.assertEquals(st1 != st3, True)
        self.assertEquals(st3 != st2, True)
        # we don't particularly care what the ordering is;  just that
        # it's usable and self-consistent
        self.assertEquals(st1 < st2, not (st2 <= st1))
        self.assertEquals(st1 < st3, not (st3 <= st1))
        self.assertEquals(st2 < st3, not (st3 <= st2))
        self.assertEquals(st1 < st2, st2 > st1)
        self.assertEquals(st1 < st3, st3 > st1)
        self.assertEquals(st2 < st3, st3 > st2)
        self.assertEquals(st1 <= st2, st2 >= st1)
        self.assertEquals(st3 <= st1, st1 >= st3)
        self.assertEquals(st2 <= st3, st3 >= st2)
        # transitivity
        bottom = min(st1, st2, st3)
        top = max(st1, st2, st3)
        mid = sorted([st1, st2, st3])[1]
        self.assertTrue(bottom < mid)
        self.assertTrue(bottom < top)
        self.assertTrue(mid < top)
        self.assertTrue(bottom <= mid)
        self.assertTrue(bottom <= top)
        self.assertTrue(mid <= top)
        self.assertTrue(bottom <= bottom)
        self.assertTrue(mid <= mid)
        self.assertTrue(top <= top)
        # interaction with other types
        self.assertEquals(st1 == 1588.602459, False)
        self.assertEquals('spanish armada' != st2, True)
        self.assertRaises(TypeError, operator.ge, st3, None)
        self.assertRaises(TypeError, operator.le, False, st1)
        self.assertRaises(TypeError, operator.lt, st1, 1815)
        self.assertRaises(TypeError, operator.gt, b'waterloo', st2)


    # XXX tests for pickling and unpickling of ST objects should go here


def test_main():
    support.run_unittest(
        RoundtripLegalSyntaxTestCase,
        IllegalSyntaxTestCase,
        CompileTestCase,
        ParserStackLimitTestCase,
        STObjectTestCase,
    )


if __name__ == "__main__":
    test_main()
