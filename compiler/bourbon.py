#!/usr/bin/env python3
# bourbon.py – BourbonScript compiler CLI

import sys
import os
import argparse
import subprocess
import shutil

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from semantic import SemanticAnalyzer, SemanticError
from interpreter import Interpreter
from codegen import LLVMCodegen

BANNER = """\
╔══════════════════════════════════════╗
║   🍪  BourbonScript Compiler v1.0   ║
║      A biscuit-powered language      ║
╚══════════════════════════════════════╝"""

def compile_and_run(source, filename, args):
    base = os.path.splitext(os.path.basename(filename))[0]

    # ── Phase 1: Lex ────────────────────────────────────────────────────────
    if args.verbose:
        print("[ Phase 1 ] Lexing...")
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except LexerError as e:
        print(f"\n{e}")
        sys.exit(1)

    if args.tokens:
        print("\n── Tokens ──")
        for tok in tokens:
            print(f"  {tok}")
        print()

    # ── Phase 2: Parse ───────────────────────────────────────────────────────
    if args.verbose:
        print("[ Phase 2 ] Parsing...")
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except ParseError as e:
        print(f"\n{e}")
        sys.exit(1)

    if args.ast:
        print("\n── AST ──")
        dump_ast(ast, indent=0)
        print()

    # ── Phase 3: Semantic Analysis ───────────────────────────────────────────
    if args.verbose:
        print("[ Phase 3 ] Semantic analysis...")
    try:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
    except SemanticError as e:
        print(f"\nSemantic errors found:")
        sys.exit(1)

    # ── Phase 4: LLVM IR generation ──────────────────────────────────────────
    if args.emit_llvm:
        if args.verbose:
            print("[ Phase 4 ] Generating LLVM IR...")
        codegen = LLVMCodegen()
        ir = codegen.generate(ast)
        ir_file = base + '.ll'
        with open(ir_file, 'w') as f:
            f.write(ir)
        print(f"\n── LLVM IR written to {ir_file} ──")
        if args.verbose:
            print(ir)
        try_compile_llvm(ir_file, base, args)
        return

    # ── Phase 5: Interpret (default) ─────────────────────────────────────────
    if args.verbose:
        print("[ Phase 4 ] Executing via interpreter...")
        print("\n── Output ──")
    try:
        interpreter = Interpreter()
        interpreter.run(ast)
    except Exception as e:
        print(f"\nRuntime Error: {e}")
        sys.exit(1)


def try_compile_llvm(ir_file, base, args):
    """Try to compile the .ll file to native binary if LLVM tools are available."""
    llc = shutil.which('llc')
    clang = shutil.which('clang') or shutil.which('gcc')

    if not llc or not clang:
        print("Note: llc/clang not found. Install LLVM to produce native binaries.")
        print(f"      You can manually run: llc {ir_file} -o {base}.s && clang {base}.s -o {base}")
        return

    obj_file = base + '.o'
    out_file = base if sys.platform != 'win32' else base + '.exe'

    print(f"\n[ Compiling ] {ir_file} → {out_file}")
    r1 = subprocess.run(['llc', '-filetype=obj', ir_file, '-o', obj_file])
    if r1.returncode != 0:
        print("LLVM compilation failed.")
        return

    compiler = shutil.which('clang') or shutil.which('gcc')
    r2 = subprocess.run([compiler, obj_file, '-o', out_file])
    if r2.returncode != 0:
        print("Linking failed.")
        return

    print(f"✓ Compiled: {out_file}")
    os.remove(obj_file)


def dump_ast(node, indent):
    pad = "  " * indent
    name = type(node).__name__
    from bon_ast import (
        ProgramNode, NumberNode, StringNode, BoolNode,
        VarAccessNode, VarAssignNode, BinaryOpNode, UnaryOpNode,
        FunctionNode, CallNode, ReturnNode, IfNode, WhileNode, PrintNode
    )
    if isinstance(node, ProgramNode):
        print(f"{pad}Program")
        for s in node.statements:
            dump_ast(s, indent + 1)
    elif isinstance(node, FunctionNode):
        print(f"{pad}func {node.name}({', '.join(node.params)})")
        for s in node.body:
            dump_ast(s, indent + 1)
    elif isinstance(node, VarAssignNode):
        kw = 'let ' if node.is_let else ''
        print(f"{pad}{kw}{node.name} =")
        dump_ast(node.value_node, indent + 1)
    elif isinstance(node, BinaryOpNode):
        print(f"{pad}BinaryOp({node.op})")
        dump_ast(node.left, indent + 1)
        dump_ast(node.right, indent + 1)
    elif isinstance(node, UnaryOpNode):
        print(f"{pad}UnaryOp({node.op})")
        dump_ast(node.node, indent + 1)
    elif isinstance(node, IfNode):
        print(f"{pad}if")
        dump_ast(node.condition, indent + 1)
        print(f"{pad}then:")
        for s in node.then_body:
            dump_ast(s, indent + 1)
        if node.else_body:
            print(f"{pad}else:")
            for s in node.else_body:
                dump_ast(s, indent + 1)
    elif isinstance(node, WhileNode):
        print(f"{pad}while")
        dump_ast(node.condition, indent + 1)
        print(f"{pad}body:")
        for s in node.body:
            dump_ast(s, indent + 1)
    elif isinstance(node, CallNode):
        print(f"{pad}call {node.name}()")
        for a in node.args:
            dump_ast(a, indent + 1)
    elif isinstance(node, ReturnNode):
        print(f"{pad}return")
        if node.value_node:
            dump_ast(node.value_node, indent + 1)
    elif isinstance(node, PrintNode):
        print(f"{pad}print")
        dump_ast(node.value_node, indent + 1)
    elif isinstance(node, NumberNode):
        print(f"{pad}Number({node.value})")
    elif isinstance(node, StringNode):
        print(f"{pad}String({node.value!r})")
    elif isinstance(node, BoolNode):
        print(f"{pad}Bool({node.value})")
    elif isinstance(node, VarAccessNode):
        print(f"{pad}Var({node.name})")
    else:
        print(f"{pad}{node}")


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        prog='bourbon',
        description='The BourbonScript Compiler 🍪 — a biscuit-powered language'
    )
    parser.add_argument('file', help='BourbonScript source file (.bon)')
    parser.add_argument('--tokens',    action='store_true', help='Dump token stream')
    parser.add_argument('--ast',       action='store_true', help='Dump AST')
    parser.add_argument('--emit-llvm', action='store_true', help='Emit LLVM IR and attempt native compile')
    parser.add_argument('--verbose',   action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.file.endswith('.bon'):
        print(f"Warning: expected a .bon file, got '{args.file}'")

    if not os.path.isfile(args.file):
        print(f"Error: file not found: '{args.file}'")
        sys.exit(1)

    with open(args.file, 'r') as f:
        source = f.read()

    print(f"\n  Compiling: {args.file}\n")
    compile_and_run(source, args.file, args)


if __name__ == '__main__':
    main()
