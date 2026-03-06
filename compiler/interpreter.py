# interpreter.py – Tree-walking interpreter for BourbonScript

from bon_ast import (
    ProgramNode, NumberNode, StringNode, BoolNode,
    VarAccessNode, VarAssignNode, BinaryOpNode, UnaryOpNode,
    FunctionNode, CallNode, ReturnNode, IfNode, WhileNode,
    BakeNode, PrintNode, OrderNode
)

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class RuntimeError_(Exception):
    def __init__(self, message):
        super().__init__(f"Runtime Error: {message}")

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def set(self, name, value):
        self.vars[name] = value

    def assign(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise RuntimeError_(f"Undefined variable '{name}'")

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError_(f"Undefined variable '{name}'")

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions = {}

    def run(self, program):
        for stmt in program.statements:
            if isinstance(stmt, FunctionNode):
                self.functions[stmt.name] = stmt
        for stmt in program.statements:
            if not isinstance(stmt, FunctionNode):
                self.eval(stmt, self.global_env)
        if 'main' in self.functions:
            self.call_function('main', [], self.global_env)

    def eval(self, node, env):
        method = f"eval_{type(node).__name__}"
        handler = getattr(self, method, None)
        if handler is None:
            raise RuntimeError_(f"Unknown node type: {type(node).__name__}")
        return handler(node, env)

    def eval_NumberNode(self, node, env):   return node.value
    def eval_StringNode(self, node, env):   return node.value
    def eval_BoolNode(self, node, env):     return node.value
    def eval_FunctionNode(self, node, env): return None

    def eval_VarAccessNode(self, node, env):
        return env.get(node.name)

    def eval_VarAssignNode(self, node, env):
        value = self.eval(node.value_node, env)
        if node.is_let:
            env.set(node.name, value)
        else:
            env.assign(node.name, value)
        return value

    def eval_BinaryOpNode(self, node, env):
        left = self.eval(node.left, env)
        right = self.eval(node.right, env)
        op = node.op
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return self._to_str(left) + self._to_str(right)
            return left + right
        if op == '-':  return left - right
        if op == '*':  return left * right
        if op == '/':
            if right == 0:
                raise RuntimeError_("Division by zero")
            return left / right if isinstance(left, float) or isinstance(right, float) else left // right
        if op == '%':  return left % right
        if op == '==': return left == right
        if op == '!=': return left != right
        if op == '<':  return left < right
        if op == '<=': return left <= right
        if op == '>':  return left > right
        if op == '>=': return left >= right
        if op == '&&': return bool(left) and bool(right)
        if op == '||': return bool(left) or bool(right)
        raise RuntimeError_(f"Unknown operator: {op}")

    def eval_UnaryOpNode(self, node, env):
        val = self.eval(node.node, env)
        if node.op == '-': return -val
        if node.op == '!': return not val
        raise RuntimeError_(f"Unknown unary operator: {node.op}")

    def eval_PrintNode(self, node, env):
        print(self._to_str(self.eval(node.value_node, env)))
        return None

    def eval_OrderNode(self, node, env):
        prompt = self._to_str(self.eval(node.prompt_node, env)) if node.prompt_node else ''
        return input(prompt)

    def eval_CallNode(self, node, env):
        args = [self.eval(arg, env) for arg in node.args]
        return self.call_function(node.name, args, env)

    def call_function(self, name, args, env):
        if name not in self.functions:
            raise RuntimeError_(f"Undefined function: '{name}'")
        func = self.functions[name]
        if len(args) != len(func.params):
            raise RuntimeError_(f"Recipe '{name}' expects {len(func.params)} args, got {len(args)}")
        func_env = Environment(parent=self.global_env)
        for (pname, ptype), val in zip(func.params, args):
            func_env.set(pname, val)
        try:
            for stmt in func.body:
                self.eval(stmt, func_env)
        except ReturnSignal as r:
            return r.value
        return None

    def eval_ReturnNode(self, node, env):
        value = self.eval(node.value_node, env) if node.value_node else None
        raise ReturnSignal(value)

    def eval_IfNode(self, node, env):
        child_env = Environment(parent=env)
        if self._truthy(self.eval(node.condition, env)):
            for stmt in node.then_body:
                self.eval(stmt, child_env)
        elif node.else_body:
            child_env2 = Environment(parent=env)
            for stmt in node.else_body:
                self.eval(stmt, child_env2)
        return None

    def eval_WhileNode(self, node, env):
        while self._truthy(self.eval(node.condition, env)):
            child_env = Environment(parent=env)
            for stmt in node.body:
                self.eval(stmt, child_env)
        return None

    def eval_BakeNode(self, node, env):
        start = int(self.eval(node.start, env))
        end   = int(self.eval(node.end, env))
        for i in range(start, end):
            child_env = Environment(parent=env)
            child_env.set(node.var, i)
            try:
                for stmt in node.body:
                    self.eval(stmt, child_env)
            except ReturnSignal:
                raise

    def _truthy(self, val):
        if val is None:            return False
        if isinstance(val, bool):  return val
        if isinstance(val, (int, float)): return val != 0
        if isinstance(val, str):   return len(val) > 0
        return True

    def _to_str(self, val):
        if isinstance(val, bool):
            return 'fresh' if val else 'stale'
        if isinstance(val, float) and val == int(val):
            return str(int(val))
        return str(val)
