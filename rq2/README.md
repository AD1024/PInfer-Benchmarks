# Satisfiability Modulo P Compiler and Interpreter

## Installation

```sh
# Get OCaml Setup
brew install opam
opam init
eval $(opam env --switch=default)
opam install dune

# Install dependencies
make deps

# Install smpi and smpc
make install
```

## Usage

### Interpreter
```sh
# Running the interpreter:
smpi examples/set.smp examples/shared.smp
# Should print:
# true
# false
# true
```

### Compiler
```sh
# Running the compiler and piping into an SMT solver like z3:
smpc examples/set.smp examples/shared.smp | z3 -in
# Should print:
# sat
# (((select arr A) true))
# (((select arr B) false))
# (((select arr C) true))
```

## Development

```sh
make format
```