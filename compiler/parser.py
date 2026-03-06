# parser.py – Recursive Descent Parser for BourbonScript
# Handles indentation-based blocks via INDENT/DEDENT tokens

from lexer import (
    Token, TT_NUMBER, TT_STRING, TT_IDENTIFIER, TT_KEYWORD,
    TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD,
    TT_EQ, TT_NEQ, TT_LT, TT_LTE, TT_GT, TT_GTE,
    TT_AND, TT_OR, TT_NOT, TT_ASSIGN,
    TT_LPAREN, TT_RPAREN, TT_COMMA, TT_COLON,
    TT_NEWLINE, TT_INDENT, TT_DEDENT, TT_EOF
)
from bon_ast import (
    ProgramNode, NumberNode, StringNode, BoolNode,
    VarAccessNode, VarAssignNode, BinaryOpNode, UnaryOpNode,
    FunctionNode, CallNode, ReturnNode, IfNode, WhileNode, PrintNode, OrderNode
)

class ParseError(Exception):
    def __init__(self, message, line):
        super().__init__(f"[Line {line}] Parse Error: {message}")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        p = self.pos + offset
        if p < len(self.tokens):
            return self.tokens[p]
        return self.tokens[-1]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def skip_newlines(self):
        while self.current().type in (TT_NEWLINE,):
            self.advance()

    def expect(self, type_, value=None):
        tok = self.current()
        if tok.type != type_:
            raise ParseError(f"Expected {type_!r}, got {tok.type!r} ({tok.value!r})", tok.line)
        if value is not None and tok.value != value:
            raise ParseError(f"Expected {value!r}, got {tok.value!r}", tok.line)
        return self.advance()

    def expect_keyword(self, kw):
        return self.expect(TT_KEYWORD, kw)

    def match(self, type_, value=None):
        tok = self.current()
        if tok.type != type_:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    # ── Program ──────────────────────────────────────────────────────────────

    def parse(self):
        self.skip_newlines()
        stmts = []
        while not self.match(TT_EOF):
            stmts.append(self.parse_statement())
            self.skip_newlines()
        return ProgramNode(stmts)

    # ── Statements ───────────────────────────────────────────────────────────

    def parse_statement(self):
        self.skip_newlines()
        tok = self.current()

        if tok.type == TT_KEYWORD:
            if tok.value == 'crumble':
                return self.parse_crumble()
            if tok.value == 'recipe':
                return self.parse_recipe()
            if tok.value == 'if':
                return self.parse_if()
            if tok.value == 'while':
                return self.parse_while()
            if tok.value == 'plate':
                return self.parse_plate()
            if tok.value == 'display':
                return self.parse_display()
            if tok.value == 'order':
                return self.parse_order()

        # Reassignment: identifier = expr
        if tok.type == TT_IDENTIFIER and self.peek().type == TT_ASSIGN:
            return self.parse_assign()

        # Expression statement (e.g. function call)
        return self.parse_expression()

    def parse_crumble(self):
        self.expect_keyword('crumble')
        name_tok = self.expect(TT_IDENTIFIER)
        self.expect(TT_ASSIGN)
        value = self.parse_expression()
        return VarAssignNode(name_tok.value, value, is_let=True)

    def parse_assign(self):
        name_tok = self.advance()
        self.expect(TT_ASSIGN)
        value = self.parse_expression()
        return VarAssignNode(name_tok.value, value, is_let=False)

    def parse_recipe(self):
        self.expect_keyword('recipe')
        name_tok = self.expect(TT_IDENTIFIER)
        self.expect(TT_LPAREN)
        params = []
        if not self.match(TT_RPAREN):
            params.append(self.expect(TT_IDENTIFIER).value)
            while self.match(TT_COMMA):
                self.advance()
                params.append(self.expect(TT_IDENTIFIER).value)
        self.expect(TT_RPAREN)
        self.expect(TT_COLON)
        body = self.parse_block()
        return FunctionNode(name_tok.value, params, body)

    def parse_if(self):
        self.expect_keyword('if')
        condition = self.parse_expression()
        self.expect(TT_COLON)
        then_body = self.parse_block()
        else_body = None
        self.skip_newlines()
        if self.match(TT_KEYWORD, 'otherwise'):
            self.advance()
            if self.match(TT_KEYWORD, 'if'):
                # "otherwise if ..." — no colon here, just chain straight into parse_if
                else_body = [self.parse_if()]
            else:
                self.expect(TT_COLON)
                else_body = self.parse_block()
        return IfNode(condition, then_body, else_body)

    def parse_while(self):
        self.expect_keyword('while')
        condition = self.parse_expression()
        self.expect(TT_COLON)
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_plate(self):
        self.expect_keyword('plate')
        if self.match(TT_NEWLINE) or self.match(TT_EOF) or self.match(TT_DEDENT):
            return ReturnNode(None)
        value = self.parse_expression()
        return ReturnNode(value)

    def parse_display(self):
        self.expect_keyword('display')
        self.expect(TT_LPAREN)
        value = self.parse_expression()
        self.expect(TT_RPAREN)
        return PrintNode(value)

    def parse_order(self):
        self.expect_keyword('order')
        self.expect(TT_LPAREN)
        # prompt is optional
        if self.match(TT_RPAREN):
            self.advance()
            return OrderNode(None)
        prompt = self.parse_expression()
        self.expect(TT_RPAREN)
        return OrderNode(prompt)

    def parse_block(self):
        """Parse an indented block: NEWLINE INDENT stmts DEDENT"""
        self.skip_newlines()
        self.expect(TT_INDENT)
        stmts = []
        while not self.match(TT_DEDENT) and not self.match(TT_EOF):
            self.skip_newlines()
            if self.match(TT_DEDENT) or self.match(TT_EOF):
                break
            stmts.append(self.parse_statement())
            # consume trailing newline after statement
            if self.match(TT_NEWLINE):
                self.advance()
        if self.match(TT_DEDENT):
            self.advance()
        return stmts

    # ── Expressions ──────────────────────────────────────────────────────────

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match(TT_OR):
            op = self.advance().value
            right = self.parse_and()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_and(self):
        left = self.parse_equality()
        while self.match(TT_AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self.current().type in (TT_EQ, TT_NEQ):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_comparison(self):
        left = self.parse_additive()
        while self.current().type in (TT_LT, TT_LTE, TT_GT, TT_GTE):
            op = self.advance().value
            right = self.parse_additive()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current().type in (TT_PLUS, TT_MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.current().type in (TT_MUL, TT_DIV, TT_MOD):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_unary(self):
        if self.match(TT_MINUS):
            op = self.advance().value
            return UnaryOpNode(op, self.parse_unary())
        if self.match(TT_NOT):
            op = self.advance().value
            return UnaryOpNode(op, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()

        if tok.type == TT_NUMBER:
            self.advance()
            return NumberNode(tok.value)

        if tok.type == TT_STRING:
            self.advance()
            return StringNode(tok.value)

        if tok.type == TT_KEYWORD and tok.value in ('true', 'false'):
            self.advance()
            return BoolNode(tok.value == 'true')

        if tok.type == TT_KEYWORD and tok.value == 'display':
            return self.parse_display()

        if tok.type == TT_KEYWORD and tok.value == 'order':
            return self.parse_order()

        if tok.type == TT_IDENTIFIER:
            if self.peek().type == TT_LPAREN:
                return self.parse_call()
            self.advance()
            return VarAccessNode(tok.value)

        if tok.type == TT_LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TT_RPAREN)
            return expr

        raise ParseError(f"Unexpected token {tok.type!r} ({tok.value!r})", tok.line)

    def parse_call(self):
        name_tok = self.advance()
        self.expect(TT_LPAREN)
        args = []
        if not self.match(TT_RPAREN):
            args.append(self.parse_expression())
            while self.match(TT_COMMA):
                self.advance()
                args.append(self.parse_expression())
        self.expect(TT_RPAREN)
        return CallNode(name_tok.value, args)
