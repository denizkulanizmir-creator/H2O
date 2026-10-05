"""H2O interpreter v0.2

Run:  python h2o.py example.h2o

Syntax:
    write "Hello"                                   prints text
    Hello1 means 4                                  defines a variable
    write Hello1                                    prints a variable
    to indicate what "name" means : input"What is your name?"
                                                    reads input into a variable
    write "Hello", write name                       a comma separates statements
"""
import re
import sys

INDICATE = re.compile(r'^to indicate what\s+"(\w+)"\s+means\s*:\s*(.+)$')


def split_outside_quotes(line, sep=","):
    parts, buf, in_quotes = [], "", False
    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
        if ch == sep and not in_quotes:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    parts.append(buf.strip())
    return [p for p in parts if p]


def is_input(expr):
    return expr.startswith("input") and (len(expr) == 5 or expr[5] in ' "')


def value(expr, variables):
    expr = expr.strip()
    if len(expr) >= 2 and expr[0] == '"' and expr[-1] == '"':
        return expr[1:-1]
    for cast in (int, float):
        try:
            return cast(expr)
        except ValueError:
            pass
    if expr in variables:
        return variables[expr]
    raise NameError(f'"{expr}" is not defined')


def read_input(expr, variables):
    rest = expr[5:].strip()
    prompt = value(rest, variables) if rest else ""
    return input(f"{prompt} ")


def run_statement(stmt, variables):
    word, _, rest = stmt.partition(" ")
    if word == "write":
        print(value(rest, variables))
        return
    match = INDICATE.match(stmt)
    if match:
        name, expr = match.group(1), match.group(2).strip()
        if is_input(expr):
            variables[name] = read_input(expr, variables)
        else:
            variables[name] = value(expr, variables)
        return
    if " means " in stmt:
        name, _, expr = stmt.partition(" means ")
        name, expr = name.strip(), expr.strip()
        if not name.isidentifier():
            raise SyntaxError(f'"{name}" is not a valid name')
        if is_input(expr):
            raise SyntaxError(
                'input needs this form: to indicate what "name" means : input"question"'
            )
        variables[name] = value(expr, variables)
        return
    raise SyntaxError(f'I do not understand "{stmt}"')


def run(source):
    variables = {}
    for number, line in enumerate(source.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            for stmt in split_outside_quotes(line):
                run_statement(stmt, variables)
        except (NameError, SyntaxError) as err:
            print(f"H2O error on line {number}: {err}")
            return


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python h2o.py program.h2o")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        run(f.read())
