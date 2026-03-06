# semantic.py – Semantic analysis for BourbonScript

from bon_ast import (
    ProgramNode, NumberNode, StringNode, BoolNode,
    VarAccessNode, VarAssignNode, BinaryOpNode, UnaryOpNode,
    FunctionNode, CallNode, ReturnNode, IfNode, WhileNode, PrintNode
)

class SemanticError(Exception):
    pass

class Scope:
    def __init__(self, parent=None):
        self.vars = set()
        self.parent = parent

    def declare(self, name):
        self.vars.add(name)

    def lookup(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.lookup(name)
        return False

class SemanticAnalyzer:
    def __init__(self):
        self.functions = {}   # name -> FunctionNode
        self.scope = Scope()
        self.errors = []
        self.in_function = False

    def error(self, msg):
        self.errors.append(SemanticError(msg))

    def analyze(self, program):
        # First pass: collect all function definitions
        for stmt in program.statements:
            if isinstance(stmt, FunctionNode):
                if stmt.name in self.functions:
                    self.error(f"Duplicate function definition: '{stmt.name}'")
                self.functions[stmt.name] = stmt

        # Second pass: analyze all statements
        for stmt in program.statements:
            self.analyze_node(stmt)

        if self.errors:
            for e in self.errors:
                print(f"  ✗ {e}")
            raise SemanticError(f"{len(self.errors)} semantic error(s) found.")

    def analyze_node(self, node):
        method = f"analyze_{type(node).__name__}"
        handler = getattr(self, method, self.generic_analyze)
        return handler(node)

    def generic_analyze(self, node):
        pass

    def analyze_ProgramNode(self, node):
        for stmt in node.statements:
            self.analyze_node(stmt)

    def analyze_FunctionNode(self, node):
        prev_in_func = self.in_function
        self.in_function = True
        child_scope = Scope(parent=self.scope)
        prev_scope = self.scope
        self.scope = child_scope
        for param in node.params:
            self.scope.declare(param)
        for stmt in node.body:
            self.analyze_node(stmt)
        self.scope = prev_scope
        self.in_function = prev_in_func

    def analyze_VarAssignNode(self, node):
        self.analyze_node(node.value_node)
        if node.is_let:
            self.scope.declare(node.name)
        else:
            if not self.scope.lookup(node.name):
                self.error(f"Variable '{node.name}' not declared before assignment")

    def analyze_VarAccessNode(self, node):
        if not self.scope.lookup(node.name):
            self.error(f"Variable '{node.name}' not defined")

    def analyze_BinaryOpNode(self, node):
        self.analyze_node(node.left)
        self.analyze_node(node.right)

    def analyze_UnaryOpNode(self, node):
        self.analyze_node(node.node)

    def analyze_CallNode(self, node):
        if node.name not in self.functions and node.name not in ('display', 'order'):
            self.error(f"Undefined function: '{node.name}'")
        else:
            if node.name in self.functions:
                expected = len(self.functions[node.name].params)
                got = len(node.args)
                if expected != got:
                    self.error(
                        f"Function '{node.name}' expects {expected} argument(s), got {got}"
                    )
        for arg in node.args:
            self.analyze_node(arg)

    def analyze_ReturnNode(self, node):
        if not self.in_function:
            self.error("'plate' used outside of a function")
        if node.value_node:
            self.analyze_node(node.value_node)

    def analyze_IfNode(self, node):
        self.analyze_node(node.condition)
        child_scope = Scope(parent=self.scope)
        prev = self.scope
        self.scope = child_scope
        for stmt in node.then_body:
            self.analyze_node(stmt)
        self.scope = prev
        if node.else_body:
            child_scope2 = Scope(parent=self.scope)
            self.scope = child_scope2
            for stmt in node.else_body:
                self.analyze_node(stmt)
            self.scope = prev

    def analyze_WhileNode(self, node):
        self.analyze_node(node.condition)
        child_scope = Scope(parent=self.scope)
        prev = self.scope
        self.scope = child_scope
        for stmt in node.body:
            self.analyze_node(stmt)
        self.scope = prev

    def analyze_PrintNode(self, node):
        self.analyze_node(node.value_node)

    def analyze_NumberNode(self, node): pass
    def analyze_StringNode(self, node): pass
    def analyze_BoolNode(self, node): pass
