from unittest import TestCase

from pyparsing import ParserElement

from pydbml.definitions.generic import expression_literal
from pydbml.parser.blueprints import ExpressionBlueprint


ParserElement.set_default_whitespace_chars(' \t\r')


class TestExpressionLiteral(TestCase):
    def test_expression_literal(self) -> None:
        val = '`SUM(amount)`'
        res = expression_literal.parse_string(val)
        self.assertIsInstance(res[0], ExpressionBlueprint)
        self.assertEqual(res[0].text, 'SUM(amount)')
