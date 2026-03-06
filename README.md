# 🍪 BourbonScript

> *"Snap it, dunk it, run it."*

A programming language inspired by the bourbon biscuit. Clean indentation-based syntax with its own biscuit-flavoured keywords.

---

## Installation

**Requirements:** Python 3.8+

```bash
# Clone the repo
git clone https://github.com/yourusername/bourbonscript
cd bourbonscript/compiler

# Run a .bon file
python3 bourbon.py program.bon
```

**Or use the standalone binary (no Python needed):**
```bash
# Linux/WSL
./bourbon program.bon

# Windows
bourbon.exe program.bon
```

---

## CLI Usage

| Command | Description |
|---------|-------------|
| `python3 bourbon.py program.bon` | Run a .bon file |
| `python3 bourbon.py program.bon --ast` | Dump the AST |
| `python3 bourbon.py program.bon --tokens` | Dump the token stream |
| `python3 bourbon.py program.bon --emit-llvm` | Generate LLVM IR |
| `python3 bourbon.py program.bon --verbose` | Verbose output |
| `python3 run_tests.py` | Run the test suite |

---

## Syntax

BourbonScript uses **indentation** to define blocks and biscuit-themed keywords.

### Hello World
```bon
recipe main():
    display("Hello, World!")
```

### Variables
```bon
crumble x = 5
crumble name = "Bourbon Biscuit"
crumble flag = true
```

### Arithmetic
```bon
crumble result = (x + 10) * 2
crumble remainder = 17 % 5
```

### If / Otherwise
```bon
if x > 0:
    display("positive")
otherwise if x == 0:
    display("zero")
otherwise:
    display("negative")
```

### While Loop
```bon
crumble i = 0
while i < 10:
    display(i)
    i = i + 1
```

### Functions
```bon
recipe add(a, b):
    plate a + b

recipe main():
    display(add(3, 4))
```

### Recursion
```bon
recipe factorial(n):
    if n <= 1:
        plate 1
    plate n * factorial(n - 1)

recipe main():
    display(factorial(6))
```

---

## Keyword Reference

| Keyword | Meaning |
|---------|---------|
| `crumble` | Declare a variable |
| `recipe` | Define a function |
| `plate` | Return a value |
| `display()` | Print to output |
| `if` | Conditional |
| `otherwise` | Else / else if |
| `while` | Loop |
| `true` / `false` | Boolean literals |

## Operators

| Operator | Meaning |
|----------|---------|
| `+` `-` `*` `/` `%` | Arithmetic |
| `==` `!=` `<` `<=` `>` `>=` | Comparison |
| `&&` `\|\|` `!` | Logical |

---

## Examples

The `examples/` folder contains:

| File | Description |
|------|-------------|
| `fizzbuzz.bon` | Classic FizzBuzz up to 20 |
| `countdown.bon` | Countdown to biscuit time |
| `calculator.bon` | add, subtract, multiply, divide, clamp |
| `power.bon` | Powers of 2 + prime sieve |
| `collatz.bon` | Collatz conjecture |
| `gcd.bon` | Greatest common divisor & LCM |
| `patterns.bon` | Triangle, square & perfect numbers |
| `guess.bon` | Binary search demo |
| `sorting.bon` | Bubble sort |

---

## Project Structure

```
bourbonscript/
├── compiler/
│   ├── bourbon.py       # CLI entry point
│   ├── lexer.py         # Tokenizer (with INDENT/DEDENT)
│   ├── parser.py        # Recursive descent parser
│   ├── bon_ast.py       # AST node definitions
│   ├── semantic.py      # Scope & type validation
│   ├── interpreter.py   # Tree-walking interpreter
│   ├── codegen.py       # LLVM IR code generator
│   ├── run_tests.py     # Automated test runner
│   └── tests/
│       ├── test_hello.bon
│       ├── test_arithmetic.bon
│       ├── test_loop.bon
│       ├── test_functions.bon
│       ├── test_fibonacci.bon
│       └── test_strings.bon
└── examples/
    └── *.bon
```

---

## Building a Binary

**Windows:**
```powershell
pip install pyinstaller
cd compiler
pyinstaller --onefile bourbon.py
# output: compiler/dist/bourbon.exe
```

**Linux / WSL:**
```bash
# Important: build from the Linux filesystem, not /mnt/c/...
cp -r compiler ~/bourbon-compiler
cd ~/bourbon-compiler
pip install pyinstaller --break-system-packages
pyinstaller --onefile bourbon.py
# output: ~/bourbon-compiler/dist/bourbon
```

---

## Roadmap

**v2:** Arrays · Strings · Modules · Imports  
**v3:** Structs · Pointers · Generics · Package manager
