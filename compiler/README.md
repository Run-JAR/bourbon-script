# 🍪 BourbonScript

> *"Snap it, dunk it, run it."*

A statically-typed, indentation-based programming language inspired by the bourbon biscuit.

---

## Installation

**Requirements:** Python 3.8+

```bash
git clone https://github.com/yourusername/bourbonscript
cd bourbonscript/compiler
python3 bourbon.py program.bon
```

**Standalone binary:**
```bash
./bourbon program.bon        # Linux
bourbon.exe program.bon      # Windows
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

### Hello World
```bon
recipe main() -> void:
    display("Hello, World!")
```

### Variables (with types)
```bon
crumble x: int = 5
crumble name: str = "Bourbon Biscuit"
crumble flag: bool = fresh
```

### Types
| Type | Meaning |
|------|---------|
| `int` | Integer number |
| `str` | String of text |
| `bool` | Boolean (`fresh` or `stale`) |
| `void` | No return value |

### Booleans
```bon
crumble hungry: bool = fresh    // true
crumble full: bool = stale      // false
```

### Functions (with typed params and return type)
```bon
recipe add(a: int, b: int) -> int:
    plate a + b

recipe greet(name: str) -> void:
    display("Hello, " + name)
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

### Range Loop (bake)
```bon
// bake i from <start> to <end>  (end is exclusive)
bake i from 0 to 10:
    display(i)
```

### Condition Loop (while)
```bon
while x != 0:
    x = x / 2
```

### User Input
```bon
crumble name: str = order("What is your name? ")
display("Hello, " + name)
```

### Recursion
```bon
recipe factorial(n: int) -> int:
    if n <= 1:
        plate 1
    otherwise:
        plate n * factorial(n - 1)
```

---

## Keyword Reference

| Keyword | Meaning |
|---------|---------|
| `crumble` | Declare a variable |
| `recipe` | Define a function |
| `plate` | Return a value |
| `display()` | Print to output |
| `order()` | Read user input |
| `if` | Conditional |
| `otherwise` | Else / else if |
| `bake` | Range loop |
| `while` | Condition loop |
| `fresh` | Boolean true |
| `stale` | Boolean false |

## Operators

| Operator | Meaning |
|----------|---------|
| `+` `-` `*` `/` `%` | Arithmetic |
| `==` `!=` `<` `<=` `>` `>=` | Comparison |
| `&&` `\|\|` `!` | Logical |

---

## Examples

| File | Description |
|------|-------------|
| `fizzbuzz.bon` | Classic FizzBuzz |
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
│   ├── lexer.py         # Tokenizer (INDENT/DEDENT)
│   ├── parser.py        # Recursive descent parser
│   ├── bon_ast.py       # AST node definitions
│   ├── semantic.py      # Type & scope validation
│   ├── interpreter.py   # Tree-walking interpreter
│   ├── codegen.py       # LLVM IR code generator
│   ├── run_tests.py     # Automated test runner
│   └── tests/
└── examples/
```

---

## Building a Binary

**Windows:**
```powershell
cd compiler
pyinstaller --onefile bourbon.py
# dist\bourbon.exe
```

**Linux / WSL:**
```bash
cp -r compiler ~/bourbon-compiler
cd ~/bourbon-compiler
pyinstaller --onefile bourbon.py
# dist/bourbon
```

---

## Roadmap

**v2:** Arrays · String operations · Modules · Imports  
**v3:** Structs · Generics · Package manager
