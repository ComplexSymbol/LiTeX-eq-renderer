lastFinishedBarHt = None


def genRender(eq, exp=False):
  global lastFinishedBarHt
  i = 0
  begWth = "" if exp == False else "^"
  lastHeight = 0
  barHt = 2 if exp else 4
  render = [[]] * (7 if exp else 10)

  while i < len(eq):
    print(f"{' ' * (i + len(str(i)) + 31)}V")
    print(f"Parsing char: '{eq[i]}' at index {i} of {eq}")
    if eq[i] == " ": pass
    
    if eq[i].isdigit() or eq[i].isalpha() or eq[i] in ("+", "-", "*", "/"):
      print(f" Appending digit '{eq[i]}'")
      char = readGlyph(begWth + eq[i])
      render = add2dArrays(render, char, AbarHt=barHt)
      lastHeight = len(char)

    elif eq[i] == "(":
      print(f" Found parenthesis")
      for j in range(1, len(eq[i:]) + 1):
        if eq[i:][:j].count("(") == eq[i:][:j].count(")"):
          print(
            f"  Found end of parenthesis at index {i + j} [contents: {eq[i:][:j]}]"
          )
          print(f"  Recursing contents {eq[i+1:][:j-2]}")

          contents = genRender(eq[i + 1 :][: j - 2], exp)
          parenHeight = len(contents) - (7 if exp else 10)
          rightParen = readGlyph(begWth + ")", parenHeight)

          render = add2dArrays(
            render,
            readGlyph(begWth + "(", -parenHeight),
            AbarHt=barHt,
            BbarHt=lastFinishedBarHt,
          )
          render = add2dArrays(
            render,
            contents,
            AbarHt=barHt,
            BbarHt=lastFinishedBarHt,
          )
          render = add2dArrays(
            render,
            rightParen,
            AbarHt=barHt,
            BbarHt=lastFinishedBarHt,
          )
          barHt = lastFinishedBarHt
          lastHeight = len(rightParen) + barHt - 4

          print(f"  Setting index i to {i + j - 1}")
          i += j - 1
          break

        if j == len(eq[i:]):
          raise Exception("Unfinished parenthesis")

    elif eq[i] == "^":
      i += 1
      print(f"Found power at index {i}")

      if eq[i] == "{":
        print(f" Found exponent brace")
        for j in range(1, len(eq[i:]) + 1):
          if eq[i:][:j].count("{") == eq[i:][:j].count("}"):
            print(
              f"  Found end of exponent brace at index {i + j} [contents: {eq[i:][:j]}]"
            )
            print(f"  Recursing contents {eq[i+1:][:j-2]}")

            contents = genRender(eq[i + 1 :][: j - 2], True)
            render = add2dArrays(
              render, contents, overlap=3 if exp else 4, relHt=lastHeight
            )

            print(f"  Setting index i to {i + j - 1}")
            i += j - 1
            break

        lastHeight = lastHeight + len(contents) - (3 if exp else 4)
        if j == len(eq[i:]):
          raise Exception("Unfinished exponential brace")

      elif eq[i].isdigit() or eq[i].isalpha():
        for j in range(0, len(eq[i:])):
          if eq[i:][j].isdigit or eq[i].isalpha():
            print(
              f" Appending power: {eq[i:][j]} at index {i + j} with relHt {lastHeight}"
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
        if eq[i:][j - 1] == "{":
          print(
            f" Found end of escape sequence/start of contents (i:{i}, j:{j}), esc: {eq[i:][:j-1]}"
          )
          
          esc = eq[i:][: j - 1]
          i += j - 1

          if esc == "\\frac":
            print("  Found fraction")
            for repeat in range(2):
              for k in range(1, len(eq[i:]) + 1):
                if eq[i:][:k].count("{") == eq[i:][:k].count("}"):
                  print(
                    f"   Found {'numerator' if repeat == 0 else 'denominator'}: {eq[i:][:k]} (Recursing!)"
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

            fraction = [
              [False] * (max(len(num[0]), len(den[0])) + 3 + (max(len(num[0]), len(den[0])) % 2))
              for _ in range(len(num) + len(den) + 2)
            ]
            fraction = merge2dArrays(
              fraction,
              num,
              (len(fraction[0]) // 2) - (len(num[0]) // 2),
              len(den) + 2,
            )
            fraction = merge2dArrays(
              fraction,
              den,
              (len(fraction[0]) // 2) - (len(den[0]) // 2),
              0,
            )
            fraction = merge2dArrays(
              fraction,
              [[True] * (len(fraction[0]) - 2)],
              1,
              len(den) + 1,
            )
            render = add2dArrays(
              render, fraction, AbarHt=barHt, BbarHt=len(den)
            )
            barHt = max(barHt, len(den))
            lastHeight = len(fraction)
            break
          
          elif esc == "\\sqrt":
            print("Found radical")
            nth = [[False, False]]
            
            for k in range(1, len(eq[i:]) + 1):
              if eq[i:][:k].count("{") == eq[i:][:k].count("}"):
                if not (False if k + i == len(eq) else eq[i:][k] == "{"):
                  break
                
                print(f"Found nth root: {eq[i:][:k]} (Recursing!)")
                nth = genRender(eq[i + 1 :][: k - 2], True)
                i += k
                break
            
            for k in range(1, len(eq[i:]) + 1):
              if eq[i:][:k].count("{") == eq[i:][:k].count("}"):
                print(f"Found radical contents: {eq[i:][:k]} (Recursing!)")
                radicand = genRender(eq[i + 1 :][: k - 2], exp)
                
                rad = [[False, False]] + ([[False, True]] * ((len(radicand) + 1) // 2))
                rad += [[True, False]] * ((len(radicand) - (len(radicand) + 1) // 2) - 4)

                radical = [[False] * (5 + len(radicand[0]) + len(nth[0])) for _ in range(max(len(radicand) + 2, len(radicand) + len(nth) - 2))]
                radical = merge2dArrays(radical, nth, 0, 4)
                radical = merge2dArrays(radical, readGlyph("rad"), len(nth[0]) - 2, 0)
                radical = merge2dArrays(radical, rad, len(nth[0]) + 1, 4)
                radical = merge2dArrays(radical, radicand, len(nth[0]) + 3, 0)
                radical = merge2dArrays(radical, [[True] * (len(radicand[0]) + 2)], len(nth[0]) + 2, len(radicand) + 1)

                render = add2dArrays(render, radical, AbarHt = barHt, BbarHt = lastFinishedBarHt)
                barHt = lastFinishedBarHt
                lastHeight = len(radical)
                i += k - 1
                break
            break

    else:
      raise Exception(f" Unidentified character: {eq[i]}")

    i += 1

  print("Removing overhead...")
  count = 0
  while True:
    if all(not p for p in render[0]):
      del render[0]
      count += 1
    else:
      break
  render.insert(0, [False] * len(render[0]))
  print(f"Removed empty overhead line [x{count - 1}]")

  print(f"Finished parsing {eq}")
  lastFinishedBarHt = barHt
  return render


def readGlyph(g, resParen=0):
  with open("glyphs.txt", "r") as glyphs:
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
  # arr = [[1 if b else 0 for b in arr[r]] for r in range(len(arr))]

  # for y in range(len(arr)):
  #  print(f"{' ' * (len(str(len(arr))) - len(str(y)))}{y}: {arr[y]}", end=",\n")

  print(f"Dimensions: {len(arr[0])}x{len(arr)}")
  print("--PRERENDER--")
  for y in range(len(arr)):
    for x in range(len(arr[0])):
      print("██" if arr[y][x] else "[]", end="")
    print()
  print("--PRERENDER--")
  
  
equation = "\\frac{\\sqrt{x}*\\sqrt{\\frac{2}{3}}}{4}+(\\sqrt{\\frac{5^6}{7}}-\\frac{8}{9^10})"
equation = r"\frac{1}{\frac{2}{\frac{sin(5)^{log(6)}}{5}}}"
equation = r"\sqrt{\frac{\sqrt{1}}{2}}+(3)^{\sqrt{4}}"
equation = r"\sqrt{\frac{\sqrt{1}{2}}{3}}+(3)^{\sqrt{4}}"
r = genRender(equation)
print2dArray(r)
