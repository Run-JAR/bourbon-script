# bon_ast.py – AST node definitions for BourbonScript

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
    def __init__(self, name, type_annotation, value_node, is_let=True):
        self.name = name
        self.type_annotation = type_annotation  # 'int', 'str', 'bool', or None
        self.value_node = value_node
        self.is_let = is_let
    def __repr__(self):
        t = f": {self.type_annotation}" if self.type_annotation else ""
        return f"VarAssignNode({'crumble ' if self.is_let else ''}{self.name}{t})"

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
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params        # list of (name, type) tuples
        self.return_type = return_type  # 'int', 'str', 'bool', 'void', or None
        self.body = body
    def __repr__(self):
        params_str = ', '.join(f"{n}: {t}" for n, t in self.params)
        return f"FunctionNode({self.name}({params_str}) -> {self.return_type})"

class CallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args
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
        self.then_body = then_body
        self.else_body = else_body
    def __repr__(self):
        return f"IfNode({self.condition})"

class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"WhileNode({self.condition})"

class BakeNode(Node):
    """bake i from <start> to <end>: — numeric range loop"""
    def __init__(self, var, start, end, body):
        self.var = var      # loop variable name (str)
        self.start = start  # expression
        self.end = end      # expression (exclusive)
        self.body = body
    def __repr__(self):
        return f"BakeNode({self.var} from {self.start} to {self.end})"

class PrintNode(Node):
    def __init__(self, value_node):
        self.value_node = value_node
    def __repr__(self):
        return f"PrintNode({self.value_node})"

class OrderNode(Node):
    def __init__(self, prompt_node):
        self.prompt_node = prompt_node
    def __repr__(self):
        return f"OrderNode({self.prompt_node})"

class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"ProgramNode([{len(self.statements)} statements])"
