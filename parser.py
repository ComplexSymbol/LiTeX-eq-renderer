equation = "(1-2)+(3-(4-5))"

operators = ("+", "-", "*", "/")


def parse(eq, surroundWithParen=False):
    print(f"\nparsing {eq}")

    # Remove whitespace
    eq = "".join(eq.split())

    # Initialize while loop and other stuff
    i = 0
    tokens = []
    numParsed = 0

    # Parse paren: always go to the first close paren and parse token that precedes it
    while eq.count(")") > 0:
        i = eq.index(")")
        numParsed += 1

        print(f"going to index {i}")
        print("- - - - -")

        contents = eq[:i].rpartition("(")[2]
        toAppend = parse(contents, True)
        tokens.append(toAppend)

        eq = eq.replace(f"({contents})", f"\\{numParsed}", 1)

    i = 0
    while i < len(eq):
        if eq[i] in operators:
            numParsed += 1

            numAndOperator = eq[: i + 1]
            tokens.append(numAndOperator)

            eq = eq.replace(numAndOperator, f"\\{numParsed}", 1)

        i += 1

    tokens.append(eq)
    eq.replace(eq, f"\\{numParsed + 1}")

    return tokens


print(f'Parsed "{parse(equation)}" from "{equation}"')
