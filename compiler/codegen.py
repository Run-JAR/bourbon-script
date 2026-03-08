# codegen.py – LLVM IR code generator for BourbonScript
# Generates .ll files that can be compiled with llc + clang/gcc

from bon_ast import (
    ProgramNode, NumberNode, StringNode, BoolNode,
    VarAccessNode, VarAssignNode, BinaryOpNode, UnaryOpNode,
    FunctionNode, CallNode, ReturnNode, IfNode, WhileNode, PrintNode
)

class CodegenError(Exception):
    pass

class LLVMCodegen:
    """
    Generates LLVM IR from a BourbonScript AST.
    
    Type system (v1):
      - Numbers  → i64 (integers) or double (floats)
      - Strings  → i8* (pointer to global string constant)
      - Bools    → i1
    
    All variables are stack-allocated with alloca.
    """

    def __init__(self):
        self.output = []           # Lines of IR
        self.globals = []          # Global string constants
        self.reg = 0               # SSA register counter
        self.label_counter = 0     # Label counter
        self.str_constants = {}    # value -> global name
        self.functions = {}        # name -> FunctionNode
        self.var_types = {}        # var name -> 'int'|'float'|'str'|'bool'
        self.current_func_vars = {}  # name -> alloca reg name

    # ── Helpers ──────────────────────────────────────────────────────────────

    def fresh_reg(self):
        self.reg += 1
        return f"%r{self.reg}"

    def fresh_label(self, prefix="lbl"):
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"

    def emit(self, line):
        self.output.append(line)

    def add_global_string(self, s):
        if s in self.str_constants:
            return self.str_constants[s]
        name = f"@str_{len(self.str_constants)}"
        # Escape newlines in the string
        escaped = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\0A')
        length = len(s) + 1  # +1 for null terminator
        self.globals.append(f'{name} = private unnamed_addr constant [{length} x i8] c"{escaped}\\00"')
        self.str_constants[s] = (name, length)
        return (name, length)

    # ── Code generation entry point ──────────────────────────────────────────

    def generate(self, program):
        # Collect functions
        for stmt in program.statements:
            if isinstance(stmt, FunctionNode):
                self.functions[stmt.name] = stmt

        # Declarations for runtime functions
        decls = [
            '; BourbonScript generated LLVM IR',
            '',
            'declare i32 @printf(i8* nocapture, ...)',
            'declare i8* @strcpy(i8*, i8*)',
            'declare i64 @strlen(i8*)',
            '',
        ]

        # Generate all functions
        func_code = []
        top_level = []

        for stmt in program.statements:
            if isinstance(stmt, FunctionNode):
                func_code.extend(self.gen_function(stmt))
            else:
                top_level.append(stmt)

        # Wrap top-level statements in a __top_level__ function if no main
        if top_level and 'main' not in self.functions:
            fake_main = FunctionNode('main', [], top_level)
            func_code.extend(self.gen_function(fake_main))
        elif top_level:
            # top-level statements before main; inject into __init__
            init_func = FunctionNode('__init__', [], top_level)
            func_code.extend(self.gen_function(init_func))

        global_decls = self.globals if self.globals else []
        lines = decls + global_decls + [''] + func_code
        return '\n'.join(lines)

    # ── Function generation ──────────────────────────────────────────────────

    def gen_function(self, node):
        lines = []
        prev_vars = self.current_func_vars
        self.current_func_vars = {}
        prev_reg = self.reg
        self.reg = 0

        param_str = ', '.join(f'i64 %p_{p}' for p in node.params)
        ret_type = 'i32' if node.name == 'main' else 'i64'
        lines.append(f'define {ret_type} @{node.name}({param_str}) {{')
        lines.append('entry:')

        # Allocate parameter slots
        for p in node.params:
            lines.append(f'  %{p} = alloca i64')
            lines.append(f'  store i64 %p_{p}, i64* %{p}')
            self.current_func_vars[p] = f'%{p}'

        stmt_lines, _ = self.gen_stmts(node.body)
        lines.extend(stmt_lines)

        if node.name == 'main':
            lines.append('  ret i32 0')
        else:
            lines.append('  ret i64 0')
        lines.append('}')
        lines.append('')

        self.current_func_vars = prev_vars
        return lines

    # ── Statement generation ─────────────────────────────────────────────────

    def gen_stmts(self, stmts):
        lines = []
        for stmt in stmts:
            sl, _ = self.gen_stmt(stmt)
            lines.extend(sl)
        return lines, None

    def gen_stmt(self, node):
        method = f"gen_{type(node).__name__}"
        handler = getattr(self, method, None)
        if handler is None:
            return [f'  ; [unimplemented: {type(node).__name__}]'], None
        return handler(node)

    def gen_VarAssignNode(self, node):
        lines = []
        val_lines, val_reg = self.gen_expr(node.value_node)
        lines.extend(val_lines)
        var_name = node.name
        if node.is_let or var_name not in self.current_func_vars:
            alloca_reg = f'%var_{var_name}'
            lines.append(f'  {alloca_reg} = alloca i64')
            self.current_func_vars[var_name] = alloca_reg
        lines.append(f'  store i64 {val_reg}, i64* {self.current_func_vars[var_name]}')
        return lines, None

    def gen_PrintNode(self, node):
        lines = []
        if isinstance(node.value_node, StringNode):
            name, length = self.add_global_string(node.value_node.value + '\n')
            fmt_ptr = self.fresh_reg()
            lines.append(f'  {fmt_ptr} = getelementptr [{length} x i8], [{length} x i8]* {name}, i64 0, i64 0')
            call_reg = self.fresh_reg()
            lines.append(f'  {call_reg} = call i32 (i8*, ...) @printf(i8* {fmt_ptr})')
        else:
            val_lines, val_reg = self.gen_expr(node.value_node)
            lines.extend(val_lines)
            fmt_str = '%lld\n'
            name, length = self.add_global_string(fmt_str)
            fmt_ptr = self.fresh_reg()
            lines.append(f'  {fmt_ptr} = getelementptr [{length} x i8], [{length} x i8]* {name}, i64 0, i64 0')
            call_reg = self.fresh_reg()
            lines.append(f'  {call_reg} = call i32 (i8*, ...) @printf(i8* {fmt_ptr}, i64 {val_reg})')
        return lines, None

    def gen_ReturnNode(self, node):
        lines = []
        if node.value_node:
            val_lines, val_reg = self.gen_expr(node.value_node)
            lines.extend(val_lines)
            lines.append(f'  ret i64 {val_reg}')
        else:
            lines.append('  ret i64 0')
        return lines, None

    def gen_IfNode(self, node):
        lines = []
        cond_lines, cond_reg = self.gen_expr(node.condition)
        lines.extend(cond_lines)

        then_lbl = self.fresh_label('then')
        else_lbl = self.fresh_label('else')
        end_lbl  = self.fresh_label('endif')

        bool_reg = self.fresh_reg()
        lines.append(f'  {bool_reg} = trunc i64 {cond_reg} to i1')
        lines.append(f'  br i1 {bool_reg}, label %{then_lbl}, label %{else_lbl if node.else_body else end_lbl}')

        lines.append(f'{then_lbl}:')
        then_lines, _ = self.gen_stmts(node.then_body)
        lines.extend(then_lines)
        lines.append(f'  br label %{end_lbl}')

        if node.else_body:
            lines.append(f'{else_lbl}:')
            else_lines, _ = self.gen_stmts(node.else_body)
            lines.extend(else_lines)
            lines.append(f'  br label %{end_lbl}')

        lines.append(f'{end_lbl}:')
        return lines, None

    def gen_WhileNode(self, node):
        lines = []
        cond_lbl = self.fresh_label('while_cond')
        body_lbl = self.fresh_label('while_body')
        end_lbl  = self.fresh_label('while_end')

        lines.append(f'  br label %{cond_lbl}')
        lines.append(f'{cond_lbl}:')

        cond_lines, cond_reg = self.gen_expr(node.condition)
        lines.extend(cond_lines)
        bool_reg = self.fresh_reg()
        lines.append(f'  {bool_reg} = trunc i64 {cond_reg} to i1')
        lines.append(f'  br i1 {bool_reg}, label %{body_lbl}, label %{end_lbl}')

        lines.append(f'{body_lbl}:')
        body_lines, _ = self.gen_stmts(node.body)
        lines.extend(body_lines)
        lines.append(f'  br label %{cond_lbl}')

        lines.append(f'{end_lbl}:')
        return lines, None

    def gen_CallNode(self, node):
        lines = []
        arg_regs = []
        for arg in node.args:
            al, ar = self.gen_expr(arg)
            lines.extend(al)
            arg_regs.append(ar)
        args_str = ', '.join(f'i64 {r}' for r in arg_regs)
        result_reg = self.fresh_reg()
        lines.append(f'  {result_reg} = call i64 @{node.name}({args_str})')
        return lines, result_reg

    # ── Expression generation ─────────────────────────────────────────────────

    def gen_expr(self, node):
        method = f"gen_{type(node).__name__}"
        handler = getattr(self, method, None)
        if handler is None:
            raise CodegenError(f"Cannot generate expression for {type(node).__name__}")
        return handler(node)

    def gen_NumberNode(self, node):
        reg = self.fresh_reg()
        val = int(node.value)
        return [f'  {reg} = add i64 0, {val}'], reg

    def gen_BoolNode(self, node):
        reg = self.fresh_reg()
        val = 1 if node.value else 0
        return [f'  {reg} = add i64 0, {val}'], reg

    def gen_StringNode(self, node):
        # Strings not supported as i64; return 0 as placeholder
        return [], '0'

    def gen_VarAccessNode(self, node):
        if node.name not in self.current_func_vars:
            raise CodegenError(f"Undefined variable '{node.name}'")
        ptr = self.current_func_vars[node.name]
        reg = self.fresh_reg()
        return [f'  {reg} = load i64, i64* {ptr}'], reg

    def gen_BinaryOpNode(self, node):
        lines = []
        ll, lr = self.gen_expr(node.left)
        rl, rr = self.gen_expr(node.right)
        lines.extend(ll)
        lines.extend(rl)
        reg = self.fresh_reg()
        op = node.op

        arith = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'sdiv', '%': 'srem'}
        cmp_map = {'==': 'eq', '!=': 'ne', '<': 'slt', '<=': 'sle', '>': 'sgt', '>=': 'sge'}

        if op in arith:
            lines.append(f'  {reg} = {arith[op]} i64 {lr}, {rr}')
        elif op in cmp_map:
            cmp_reg = self.fresh_reg()
            lines.append(f'  {cmp_reg} = icmp {cmp_map[op]} i64 {lr}, {rr}')
            lines.append(f'  {reg} = zext i1 {cmp_reg} to i64')
        elif op == '&&':
            lines.append(f'  {reg} = and i64 {lr}, {rr}')
        elif op == '||':
            lines.append(f'  {reg} = or i64 {lr}, {rr}')
        else:
            raise CodegenError(f"Unknown binary op: {op}")
        return lines, reg

    def gen_UnaryOpNode(self, node):
        lines, val_reg = self.gen_expr(node.node)
        reg = self.fresh_reg()
        if node.op == '-':
            lines.append(f'  {reg} = sub i64 0, {val_reg}')
        elif node.op == '!':
            tmp = self.fresh_reg()
            lines.append(f'  {tmp} = icmp eq i64 {val_reg}, 0')
            lines.append(f'  {reg} = zext i1 {tmp} to i64')
        else:
            raise CodegenError(f"Unknown unary op: {node.op}")
        return lines, reg
