def genRender(eq, exp=False):
    i = 0
    mode = ""
    begWth = "" if exp == False else "^"
    lastHeight = 0
    barHt = 2 if exp else 4
    render = [[]] * (7 if exp else 10)

    while i < len(eq):
        print(f"Parsing char: '{eq[i]}' at index {i} of {eq}")

        if eq[i].isdigit() or eq[i] in ("+", "-", "*", "/"):
            print(f"  Appending digit '{eq[i]}'")
            char = readGlyph(begWth + eq[i])
            render = add2dArrays(render, char, AbarHt=barHt)
            lastHeight = len(char)

        elif eq[i] == "(":
            print(f"  Found parenthesis")
            for j in range(1, len(eq[i:]) + 1):
                if eq[i:][:j].count("(") == eq[i:][:j].count(")"):
                    print(
                        f"    Found end of parenthesis at index {i + j} [contents: {eq[i:][:j]}]"
                    )
                    print(f"    Recursing contents {eq[i+1:][:j-2]}")

                    contents = genRender(eq[i + 1 :][: j - 2], exp)
                    print(f"Adding {len(contents) - 10} to paren size")

                    parenHeight = len(contents) - (7 if exp else 10)
                    rightParen = readGlyph(begWth + ")", parenHeight)

                    render = add2dArrays(
                        render, readGlyph(begWth + "(", -parenHeight), AbarHt=barHt
                    )
                    render = add2dArrays(render, contents, AbarHt=barHt)
                    render = add2dArrays(render, rightParen, AbarHt=barHt)
                    lastHeight = len(rightParen)

                    print(f"    Setting index i to {i + j - 1}")
                    i += j - 1
                    break

                if j == len(eq[i:]):
                    raise Exception("Unfinished parenthesis")

        elif eq[i] == "^":
            i += 1
            print(f"Found power at index {i}")

            if eq[i] == "{":
                print(f"  Found exponent brace")
                for j in range(1, len(eq[i:]) + 1):
                    if eq[i:][:j].count("{") == eq[i:][:j].count("}"):
                        print(
                            f"    Found end of exponent brace at index {i + j} [contents: {eq[i:][:j]}]"
                        )
                        print(f"    Recursing contents {eq[i+1:][:j-2]}")

                        contents = genRender(eq[i + 1 :][: j - 2], True)
                        render = add2dArrays(
                            render, contents, overlap=3 if exp else 4, relHt=lastHeight
                        )

                        print(f"    Setting index i to {i + j - 1}")
                        i += j - 1
                        break

                lastHeight = lastHeight + len(contents) - (3 if exp else 4)
                if j == len(eq[i:]):
                    raise Exception("Unfinished exponential brace")

            elif eq[i].isdigit():
                for j in range(0, len(eq[i:])):
                    if eq[i:][j].isdigit():
                        print(
                            f"  Appending power: {eq[i:][j]} at index {i + j} with relHt {lastHeight}"
                        )
                        thisExp = readGlyph("^" + eq[i:][j])
                        render = add2dArrays(
                            render, thisExp, overlap=3 if exp else 4, relHt=lastHeight
                        )
                    else:
                        j -= 1
                        break

                lastHeight = (
                    (max(len(render), len(thisExp)) if exp else lastHeight)
                    + len(thisExp)
                    - (3 if exp else 4)
                )
                i += j

        elif eq[i] == "\\":
            print("Found escape sequence")
            for j in range(1, len(eq[i:]) + 1):
                if eq[i:][j].isdigit():
                    print(
                        f"  Found end of escape sequence/start of contents (i:{i}, j:{j}), esc: {eq[i:][:j-1]}"
                    )

                    if eq[i:][j - 1] == "{":
                        esc = eq[i:][: j - 1]

                        if esc == "\\frac":
                            print("    Found fraction")
                            i += j - 1

                            for repeat in range(2):
                                for k in range(1, len(eq[i:]) + 1):
                                    if eq[i:][:k].count("{") == eq[i:][:k].count("}"):
                                        print(
                                            f"      Found {'numerator' if repeat == 0 else 'denominator'}: {eq[i:][:k]} (Recursing!)"
                                        )
                                        num = (
                                            genRender(eq[i + 1 :][: k - 2], True)
                                            if repeat == 0
                                            else num
                                        )
                                        den = (
                                            genRender(eq[i + 1 :][: k - 2], True)
                                            if repeat == 1
                                            else None
                                        )

                                        print(f"Setting i to {i + k}")
                                        i += k
                                        break

                            i -= 1
                            fraction = [
                                [False] * (max(len(num[0]), len(den[0])) + 4)
                                for _ in range(len(num) + len(den) + 2)
                            ]
                            fraction = merge2dArrays(
                                fraction,
                                num,
                                -(-(len(fraction[0])) // 2) - (len(num[0]) // 2),
                                len(den) + 2,
                            )
                            fraction = merge2dArrays(
                                fraction,
                                den,
                                -(-(len(fraction[0])) // 2) - (len(den[0]) // 2),
                                0,
                            )
                            fraction = merge2dArrays(
                                fraction,
                                [[True] * (len(fraction[0]) - 3)],
                                2,
                                len(den) + 1,
                            )
                            render = add2dArrays(
                                render, fraction, AbarHt=barHt, BbarHt=len(den)
                            )
                            barHt = len(den)
                            lastHeight = len(fraction)

                        break

                    print(f"  ")

        else:
            print(f"  Unidentified character: {eq[i]}")

        print2dArray(render)
        i += 1
        if i < len(eq):
            print(f"{' ' * (i + len(str(i)) + 31)}V")

    print(f"Finished parsing {eq}")
    return render


def readGlyph(g, resParen=0):
    with open("/lib/glyphs.txt", "r") as glyphs:
        glyphs = glyphs.readlines()

        for i in range(len(glyphs)):
            line = glyphs[i].replace("\n", "")

            if line.endswith(":") and line.startswith(g):
                line = line.replace(g, "", 1).replace(":", "")

                width = 6 if len(line) == 0 else int(line.rpartition("x")[0])
                height = 10 if len(line) == 0 else int(line.rpartition("x")[2])

                glyph = [[False] * width for _ in range(height)]

                for y in range(height):
                    i += 1

                    line = [
                        True if digit == "1" else False
                        for digit in bin(int(glyphs[i]))[2:]
                    ]
                    line = [False] * (width - len(line)) + line
                    glyph[y] = line

                for p in range(abs(resParen)):
                    glyph.insert(
                        4,
                        [False, True, False, False]
                        if resParen < 0
                        else [False, False, False, True],
                    )

                return glyph

    raise Exception(f"Glyph not found '{g}'")


def add2dArrays(a, b, overlap=-1, relHt=-1, AbarHt=-1, BbarHt=-1):
    if relHt == -1:
        relHt = len(a)
    if AbarHt == -1:
        AbarHt = (len(a) // 2) - 1
    if BbarHt == -1:
        BbarHt = (len(b) // 2) - 1
    diff = AbarHt - BbarHt

    print(
        f"Add2dArrays ARGS: overlap: {overlap}, relHt: {relHt}, AbarHt: {AbarHt}, BbarHt: {BbarHt}, diff: {diff}"
    )

    newArray = [
        [False] * (len(a[0]) + len(b[0]))
        for _ in range(
            max(
                max(len(a), len(b)) + ((len(b) - BbarHt - 1) - (len(a) - AbarHt - 1)),
                len(a),
                len(b),
            )
            if overlap == -1
            else max(len(a), relHt + len(b) - overlap)
        )
    ]
    newArray = merge2dArrays(newArray, a, 0, abs(diff) if diff < 0 else 0)
    newArray = merge2dArrays(
        newArray,
        b,
        len(a[0]),
        (diff if diff > 0 else 0) if overlap == -1 else (relHt - overlap),
    )

    return newArray


def merge2dArrays(a, b, x, y):
    y = len(a) - y
    for h in range(len(a)):
        toMerge = (
            [False] * len(a[0])
            if not (h <= y and h > y - len(b))
            else ([False] * x) + b[h - y] + ([False] * (len(a[0]) - len(b[0]) - x))
        )
        a[h] = [max(a[h][i], toMerge[i]) for i in range(len(toMerge))]

    return a


def print2dArray(arr):
    arr = [[1 if b else 0 for b in arr[r]] for r in range(len(arr))]

    for y in range(len(arr)):
        print(f"{' ' * (len(str(len(arr))) - len(str(y)))}{y}: {arr[y]}", end=",\n")

    print(f"Dimensions: {len(arr[0])}x{len(arr)}")
    print("--PRERENDER--")
    for y in range(len(arr)):
        for x in range(len(arr[0])):
            print("█" * 2 if arr[y][x] else " " * 2, end="")
        print()
    print("--PRERENDER--")
