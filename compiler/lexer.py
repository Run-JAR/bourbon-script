# lexer.py – Tokenizer for BourbonScript

TT_NUMBER     = 'NUMBER'
TT_STRING     = 'STRING'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD    = 'KEYWORD'
TT_PLUS       = 'PLUS'
TT_MINUS      = 'MINUS'
TT_MUL        = 'MUL'
TT_DIV        = 'DIV'
TT_MOD        = 'MOD'
TT_EQ         = 'EQ'
TT_NEQ        = 'NEQ'
TT_LT         = 'LT'
TT_LTE        = 'LTE'
TT_GT         = 'GT'
TT_GTE        = 'GTE'
TT_AND        = 'AND'
TT_OR         = 'OR'
TT_NOT        = 'NOT'
TT_ASSIGN     = 'ASSIGN'
TT_ARROW      = 'ARROW'   # ->
TT_LPAREN     = 'LPAREN'
TT_RPAREN     = 'RPAREN'
TT_COMMA      = 'COMMA'
TT_COLON      = 'COLON'
TT_NEWLINE    = 'NEWLINE'
TT_INDENT     = 'INDENT'
TT_DEDENT     = 'DEDENT'
TT_EOF        = 'EOF'

KEYWORDS = {
    'crumble', 'recipe', 'if', 'otherwise', 'while', 'plate',
    'fresh', 'stale', 'display', 'order',
    'bake', 'from', 'to',
    'int', 'str', 'bool', 'void',
}

class Token:
    def __init__(self, type_, value=None, line=0):
        self.type = type_
        self.value = value
        self.line = line
    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type}, {self.value!r})"
        return f"Token({self.type})"

class LexerError(Exception):
    def __init__(self, message, line):
        super().__init__(f"[Line {line}] Lexer Error: {message}")

class Lexer:
    def __init__(self, source):
        self.source = source if source.endswith('\n') else source + '\n'
        self.pos = 0
        self.line = 1
        self.tokens = []
        self.indent_stack = [0]

    def current(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def peek(self, offset=1):
        p = self.pos + offset
        if p < len(self.source):
            return self.source[p]
        return None

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def skip_comment(self):
        while self.current() and self.current() != '\n':
            self.advance()

    def read_number(self):
        start = self.pos
        has_dot = False
        while self.current() and (self.current().isdigit() or (self.current() == '.' and not has_dot)):
            if self.current() == '.':
                has_dot = True
            self.advance()
        num_str = self.source[start:self.pos]
        return float(num_str) if has_dot else int(num_str)

    def read_string(self, quote_char):
        self.advance()
        result = []
        while self.current() and self.current() != quote_char:
            if self.current() == '\\':
                self.advance()
                esc = self.advance()
                result.append({'n': '\n', 't': '\t', '\\': '\\', '"': '"', "'": "'"}.get(esc, esc))
            else:
                result.append(self.advance())
        if not self.current():
            raise LexerError("Unterminated string literal", self.line)
        self.advance()
        return ''.join(result)

    def read_identifier(self):
        start = self.pos
        while self.current() and (self.current().isalnum() or self.current() == '_'):
            self.advance()
        return self.source[start:self.pos]

    def tokenize(self):
        at_line_start = True

        while self.pos < len(self.source):
            ch = self.current()

            if at_line_start:
                at_line_start = False
                level = 0
                while self.current() in (' ', '\t'):
                    level += 4 if self.current() == '\t' else 1
                    self.advance()

                if self.current() == '\n':
                    self.advance()
                    at_line_start = True
                    continue

                if self.current() == '/' and self.peek() == '/':
                    self.skip_comment()
                    if self.current() == '\n':
                        self.advance()
                    at_line_start = True
                    continue

                if self.current() is None:
                    break

                current_level = self.indent_stack[-1]
                if level > current_level:
                    self.indent_stack.append(level)
                    self.tokens.append(Token(TT_INDENT, level, self.line))
                elif level < current_level:
                    while self.indent_stack[-1] > level:
                        self.indent_stack.pop()
                        self.tokens.append(Token(TT_DEDENT, level, self.line))
                    if self.indent_stack[-1] != level:
                        raise LexerError("Inconsistent indentation", self.line)

                ch = self.current()

            if ch in (' ', '\t', '\r'):
                self.advance()
                continue

            line = self.line

            if ch == '\n':
                self.advance()
                self.tokens.append(Token(TT_NEWLINE, None, line))
                at_line_start = True
                continue

            if ch == '/' and self.peek() == '/':
                self.skip_comment()
                continue

            if ch.isdigit():
                val = self.read_number()
                self.tokens.append(Token(TT_NUMBER, val, line))
                continue

            if ch in ('"', "'"):
                val = self.read_string(ch)
                self.tokens.append(Token(TT_STRING, val, line))
                continue

            if ch.isalpha() or ch == '_':
                ident = self.read_identifier()
                if ident in KEYWORDS:
                    self.tokens.append(Token(TT_KEYWORD, ident, line))
                else:
                    self.tokens.append(Token(TT_IDENTIFIER, ident, line))
                continue

            # Three-char: check nothing needed

            # Two-char operators
            two = ch + (self.peek() or '')
            if two == '->':
                self.advance(); self.advance()
                self.tokens.append(Token(TT_ARROW, '->', line))
                continue

            two_map = {
                '==': TT_EQ, '!=': TT_NEQ, '<=': TT_LTE,
                '>=': TT_GTE, '&&': TT_AND, '||': TT_OR,
            }
            if two in two_map:
                self.advance(); self.advance()
                self.tokens.append(Token(two_map[two], two, line))
                continue

            one_map = {
                '+': TT_PLUS, '-': TT_MINUS, '*': TT_MUL, '/': TT_DIV,
                '%': TT_MOD, '=': TT_ASSIGN, '<': TT_LT, '>': TT_GT,
                '!': TT_NOT, '(': TT_LPAREN, ')': TT_RPAREN,
                ',': TT_COMMA, ':': TT_COLON,
            }
            if ch in one_map:
                self.advance()
                self.tokens.append(Token(one_map[ch], ch, line))
                continue

            raise LexerError(f"Unexpected character: {ch!r}", self.line)

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TT_DEDENT, 0, self.line))

        self.tokens.append(Token(TT_EOF, None, self.line))
        return self.tokens
