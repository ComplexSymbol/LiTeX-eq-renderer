def generateRender(equation):
    i = 0
    mode = ""
    keepMode = False

    while i < len(equation):
        chr = equation[i]

        if chr == "\\":
            for c in equation[(i + 1) :]:
                if c == "{":
                    keepMode = True
                    break

                if c.isalpha():
                    mode += c

                else:
                    raise Exception(
                        f'Parsing error at index {i}:{c} of "{equation}". (Unfinished mode: \\{mode})'
                    )

        elif chr == "}":
            mode = ""
            keepMode = False

        elif chr == "^":
            mode = "exp"

        elif chr.isdigit:
            # TODO TODO TODO

            if not keepMode:
                mode = ""

        i += 1


def readGlyph(g):
    with open("/lib/glyphs.txt", "r") as glyphs:
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

                print2dArray(glyph)
                return glyph

    raise Exception(f"Glyph not found ({g})")


def add2dArrays(a, b, exp=False):
    newArray = [[0] * len(a[0] + b[0]) for _ in range(max(len(a), len(b)))]

    for y in range(len(newArray)):
        if exp:
            newArray[y] = a[y] + ([0] * len(b[0]) if y >= len(b) else b[y])
        else:
            newArray[y] = (
                [0] * len(a[0])
                if y < (len(newArray) - len(a))
                else a[y - (len(newArray) - len(a))]
            ) + (
                [0] * len(b[0])
                if y < (len(newArray) - len(b))
                else b[y - (len(newArray) - len(b))]
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

    print2dArray(a)
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
