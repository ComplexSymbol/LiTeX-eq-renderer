def genRender(eq):
    i = 0
    mode = ""
    render = []

    while i < len(eq):
        if eq[i].isdigit() or eq[i] in ("+", "-", "*", "/"):
            render.append(readGlyph(eq[i]))

        elif eq[i] == "(":
            for j in range(1, len(eq[i:]) + 1):
                if eq[i:][:j].count("(") == eq[i:][:j].count(")"):
                    render.append(readGlyph("("))

                    for r in genRender(eq[i:][:j][1:][:-1]):
                        render.append(r)
                    eq = eq.replace(eq[i:][:j], "", 1)

                    render.append(readGlyph(")"))
                    i -= 1
                    break

                if j == len(eq[i:]):
                    raise Exception("Unfinished  parenthesis")

        elif eq[i] == "^":
            if eq[i + 1] == '{':
                i += 1
                for j in range(1, len(eq[i:]) + 1):
                    if eq[i:][:j].count("{") == eq[i:][:j].count("}"):
                        for r in genRender(eq[i:][:j][1:][:-1]):
                            render.append(r)
                        eq = eq.replace(eq[i:][:j], "", 1)

                        i -= 1
                        break

                if j == len(eq[i:]):
                    raise Exception("Unfinished  brace")

            elif eq[i].isdigit():


        i += 1

    return render


def readGlyph(g):
    with open("glyphs.txt", "r") as glyphs:
        glyphs = glyphs.readlines()

        for i in range(len(glyphs)):
            line = glyphs[i].replace("\n", "")

            if line.endswith(":") and line.startswith(g):
                line = line.replace(g, "").replace(":", "")

                width = 6 if len(line) == 0 else int(line.rpartition("x")[0])
                height = 10 if len(line) == 0 else int(line.rpartition("x")[2])

                glyph = [[0] * width for _ in range(height)]

                for y in range(height):
                    i += 1

                    line = [
                        1 if digit == "1" else 0 for digit in bin(int(glyphs[i]))[2:]
                    ]
                    line = [0] * (width - len(line)) + line

                    for x in range(width):
                        glyph[y][x] = line[x]

                return glyph

    raise Exception(f"Glyph  not  found  '{g}'")


def add2dArrays(a, b, overlap = None, resizeAParenTo = None, resizeBParenTo = None, relativeHA = None):
    if relativeHA == None:
        relativeHA = len(a)

    if resizeAParenTo != None:
        for _ in range(resizeAParenTo - len(a)):
            a.insert(3, [0, 1, 0, 0])

    if resizeBParenTo != None:
        for _ in range(resizeAParenTo - len(b)):
            a.insert(3, [0, 0, 0, 1])

    newArray = [
        [0] * len(a[0] + b[0])
        for _ in range(
            max(len(b), len(a)) if overlap == None else (len(a) + len(b) - overlap)
        )
    ]

    newArray = mergeBitmaps(newArray, a, 0, 0)

    newArray = mergeBitmaps(
        newArray, b, len(a[0]), 0 if overlap == None else (relativeHA - overlap)
    )

    return newArray



def merge2dArrays(a, b, Mx, My):
    My = len(a) - My
    for y in range(len(a)):
        toMerge = (
            [0] * len(a[0])
            if not (y <= My and y > My - len(b))
            else ([0] * Mx) + b[y - My] + ([0] * (len(a[0]) - len(b[0]) - Mx))
        )

    a[y] = [max(a[y][i], toMerge[i]) for i in range(len(toMerge))]

    return a


def print2dArray(arr):
    for y in range(len(arr)):
        for x in range(len(arr[0])):
            print(arr[y][x], end=" ")
        print()

    for y in range(len(arr)):
        print(f"{y}: {arr[y]}", end=",\n")

    print("--PRERENDER-- **NOT TO SCALE**")
    for y in range(len(arr)):
        for x in range(len(arr[0])):
            print("█" if arr[y][x] == 1 else " ", end="")
        print()
    print("--PRERENDER--")


rendered = [[]]
for k in genRender("1+2-(3-(4-5)^2-6)"):
    rendered = add2dArrays(rendered, k)

print2dArray(rendered)
