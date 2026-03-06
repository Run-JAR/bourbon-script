# ast.py – Abstract Syntax Tree node definitions for BourbonScript

class Node:
    pass

class NumberNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"

class StringNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"StringNode({self.value!r})"

class BoolNode(Node):
    def __init__(self, value):
        self.value = value  # True or False

    def __repr__(self):
        return f"BoolNode({self.value})"

class VarAccessNode(Node):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"VarAccessNode({self.name})"

class VarAssignNode(Node):
    def __init__(self, name, value_node, is_let=True):
        self.name = name
        self.value_node = value_node
        self.is_let = is_let  # True = declaration, False = reassignment

    def __repr__(self):
        return f"VarAssignNode({'let ' if self.is_let else ''}{self.name} = {self.value_node})"

class BinaryOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOpNode({self.left} {self.op} {self.right})"

class UnaryOpNode(Node):
    def __init__(self, op, node):
        self.op = op
        self.node = node

    def __repr__(self):
        return f"UnaryOpNode({self.op}{self.node})"

class FunctionNode(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of param name strings
        self.body = body      # list of statements

    def __repr__(self):
        return f"FunctionNode({self.name}({', '.join(self.params)}))"

class CallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args  # list of expression nodes

    def __repr__(self):
        return f"CallNode({self.name}(...))"

class ReturnNode(Node):
    def __init__(self, value_node):
        self.value_node = value_node

    def __repr__(self):
        return f"ReturnNode({self.value_node})"

class IfNode(Node):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body    # list of statements
        self.else_body = else_body    # list of statements or None

    def __repr__(self):
        return f"IfNode({self.condition})"

class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body  # list of statements

    def __repr__(self):
        return f"WhileNode({self.condition})"

class PrintNode(Node):
    def __init__(self, value_node):
        self.value_node = value_node

    def __repr__(self):
        return f"PrintNode({self.value_node})"

class OrderNode(Node):
    def __init__(self, prompt_node):
        self.prompt_node = prompt_node  # optional prompt string

    def __repr__(self):
        return f"OrderNode({self.prompt_node})"

class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode([{len(self.statements)} statements])"
