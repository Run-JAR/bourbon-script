# semantic.py – Semantic analysis for BourbonScript

from bon_ast import (
    ProgramNode, NumberNode, StringNode, BoolNode,
    VarAccessNode, VarAssignNode, BinaryOpNode, UnaryOpNode,
    FunctionNode, CallNode, ReturnNode, IfNode, WhileNode,
    BakeNode, PrintNode, OrderNode
)

class SemanticError(Exception):
    pass

BUILTIN_TYPES = {'int', 'str', 'bool', 'void', None}

TYPE_OF = {
    NumberNode: 'int',
    StringNode: 'str',
    BoolNode:   'bool',
}

class Scope:
    def __init__(self, parent=None):
        self.vars = {}  # name -> type
        self.parent = parent

    def declare(self, name, type_):
        self.vars[name] = type_

    def lookup(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def exists(self, name):
        return self.lookup(name) is not None

class SemanticAnalyzer:
    def __init__(self):
        self.functions = {}
        self.scope = Scope()
        self.errors = []
        self.current_return_type = None

    def error(self, msg):
        self.errors.append(SemanticError(msg))

    def analyze(self, program):
        for stmt in program.statements:
            if isinstance(stmt, FunctionNode):
                if stmt.name in self.functions:
                    self.error(f"Duplicate function definition: '{stmt.name}'")
                self.functions[stmt.name] = stmt

        for stmt in program.statements:
            self.analyze_node(stmt)

        if self.errors:
            for e in self.errors:
                print(f"  ✗ {e}")
            raise SemanticError(f"{len(self.errors)} semantic error(s) found.")

    def analyze_node(self, node):
        method = f"analyze_{type(node).__name__}"
        handler = getattr(self, method, lambda n: None)
        return handler(node)

    def analyze_FunctionNode(self, node):
        prev_return = self.current_return_type
        self.current_return_type = node.return_type
        child = Scope(parent=self.scope)
        prev = self.scope
        self.scope = child
        for pname, ptype in node.params:
            self.scope.declare(pname, ptype)
        has_plate = self._check_has_plate(node.body)
        if node.return_type and node.return_type != 'void' and not has_plate:
            self.error(f"Recipe '{node.name}' has return type '{node.return_type}' but not all branches have a plate statement")
        for stmt in node.body:
            self.analyze_node(stmt)
        self.scope = prev
        self.current_return_type = prev_return

    def _check_has_plate(self, stmts):
        """Check that every code path ends with a plate."""
        for stmt in reversed(stmts):
            if isinstance(stmt, ReturnNode):
                return True
            if isinstance(stmt, IfNode):
                if stmt.else_body:
                    if self._check_has_plate(stmt.then_body) and self._check_has_plate(stmt.else_body):
                        return True
        return False

    def analyze_VarAssignNode(self, node):
        self.analyze_node(node.value_node)
        if node.is_let:
            self.scope.declare(node.name, node.type_annotation)
        else:
            if not self.scope.exists(node.name):
                self.error(f"Variable '{node.name}' not declared before assignment")

    def analyze_VarAccessNode(self, node):
        if not self.scope.exists(node.name):
            self.error(f"Variable '{node.name}' not defined")

    def analyze_BinaryOpNode(self, node):
        self.analyze_node(node.left)
        self.analyze_node(node.right)

    def analyze_UnaryOpNode(self, node):
        self.analyze_node(node.node)

    def analyze_CallNode(self, node):
        builtins = ('display', 'order')
        if node.name not in self.functions and node.name not in builtins:
            self.error(f"Undefined function: '{node.name}'")
        elif node.name in self.functions:
            expected = len(self.functions[node.name].params)
            got = len(node.args)
            if expected != got:
                self.error(f"Recipe '{node.name}' expects {expected} argument(s), got {got}")
        for arg in node.args:
            self.analyze_node(arg)

    def analyze_ReturnNode(self, node):
        if node.value_node:
            self.analyze_node(node.value_node)

    def analyze_IfNode(self, node):
        self.analyze_node(node.condition)
        child = Scope(parent=self.scope)
        prev = self.scope
        self.scope = child
        for stmt in node.then_body:
            self.analyze_node(stmt)
        self.scope = prev
        if node.else_body:
            child2 = Scope(parent=self.scope)
            self.scope = child2
            for stmt in node.else_body:
                self.analyze_node(stmt)
            self.scope = prev

    def analyze_WhileNode(self, node):
        self.analyze_node(node.condition)
        child = Scope(parent=self.scope)
        prev = self.scope
        self.scope = child
        for stmt in node.body:
            self.analyze_node(stmt)
        self.scope = prev

    def analyze_BakeNode(self, node):
        self.analyze_node(node.start)
        self.analyze_node(node.end)
        child = Scope(parent=self.scope)
        prev = self.scope
        self.scope = child
        self.scope.declare(node.var, 'int')
        for stmt in node.body:
            self.analyze_node(stmt)
        self.scope = prev

    def analyze_PrintNode(self, node):
        self.analyze_node(node.value_node)

    def analyze_OrderNode(self, node):
        if node.prompt_node:
            self.analyze_node(node.prompt_node)

    def analyze_NumberNode(self, node): pass
    def analyze_StringNode(self, node): pass
    def analyze_BoolNode(self, node):   pass
