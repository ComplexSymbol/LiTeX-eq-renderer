import Evaluator

lastFinishedBarHt = None
logging = False

def genRender(eq, exp=False):
  global lastFinishedBarHt
  i = 0
  begWth = "" if exp == False else "^"
  lastHeight = 0
  barHt = 2 if exp else 4
  render = [[]] * (7 if exp else 10)
  hang = 0

  while i < len(eq):
    print(f"{' ' * (i + len(str(i)) + 31)}V")
    print(f"Parsing char: '{eq[i]}' at index {i} of {eq} with hang {hang}")
    if eq[i] == " ":
      i += 1
      continue
    
    if eq[i].isdigit() or eq[i].isalpha() or eq[i] in ("+", "-", "*", "/", "=", ".", "_"):
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
          parenHeight = max(0, len(contents) - (7 if exp else 10))
          rightParen = readGlyph(begWth + ")", parenHeight)

          render = add2dArrays(
            render,
            readGlyph(begWth + "(", -parenHeight),
            AbarHt=barHt,
            BbarHt=lastFinishedBarHt,
          )
          barHt = max(barHt, lastFinishedBarHt)
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
          lastHeight = parenHeight + (7 if exp else 10) + hang

          print(f"  Setting index i to {i + j - 1}")
          i += j - 1
          break

        if j == len(eq[i:]):
          raise Exception("Unfinished parenthesis")

    elif eq[i] == "^" or eq[i] == "_":
      pwr = eq[i] == "^"
      i += 1
      print(f"Found exponent/subscript at index {i}")

      if eq[i] == "{":
        print(f" Found exponent/subscript brace")
        for j in range(1, len(eq[i:]) + 1):
          if eq[i:][:j].count("{") == eq[i:][:j].count("}"):
            print(f"  Found end of exponent/subscript brace at index {i + j} [contents: {eq[i:][:j]}]")
            print(f"  Recursing contents {eq[i+1:][:j-2]}")

            contents = genRender(eq[i + 1 :][: j - 2], True)
            if pwr:
              render = add2dArrays(
                render, contents, overlap=3 if exp else 4, relHt=lastHeight
              )
            else:
              render = add2dArrays(render, contents, AbarHt=barHt, BbarHt=len(contents) - (2 if exp else 0), add = len(contents) - barHt)
              barHt += abs(min(barHt - len(contents), 0))

            print(f"  Setting index i to {i + j - 1}")
            i += j - 1
            break

        lastHeight = lastHeight + ((len(contents) - (3 if exp else 4)) if pwr else 2)
        if j == len(eq[i:]):
          raise Exception("Unfinished exponential brace")
    
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
              [False] * (max(len(num[0]), len(den[0])) + 2 + (max(len(num[0]), len(den[0])) % 2))
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
              [[True] * (len(fraction[0]) - 1)],
              1,
              len(den) + 1,
            )
            render = add2dArrays(
              render, fraction, AbarHt=barHt, BbarHt=len(den)
            )
            barHt = max(barHt, len(den)) + hang
            lastHeight = len(fraction) + hang
            i -= 1
            break
          
          elif esc == "\\sqrt":
            print("Found radical")
            nth = [[False, False]]
            
            for k in range(1, len(eq[i:]) + 1):
              if eq[i:][:k].count("{") == eq[i:][:k].count("}"):
                if not (False if k + i == len(eq) else eq[i:][k] == "{"):
                  break
                
                print(f"Found nth root: {eq[i:][:k]} (Recursing!)")
                if eq[i + 1 :][: k - 2] != "2":
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
                radical = merge2dArrays(radical, [[True] * (len(radicand[0]) + 3)], len(nth[0]) + 2, len(radicand) + 1)
                radical = merge2dArrays(radical, [[True], [True]], len(radicand[0]) + len(nth[0]) + 4, len(radicand) - 1)
                
                render = add2dArrays(render, radical, AbarHt = barHt, BbarHt = lastFinishedBarHt)
                barHt = max(barHt, lastFinishedBarHt) + hang
                lastHeight = len(radical) + hang
                i += k - 1
                break
            break
        
        elif eq[i:][j - 1].isdigit() or eq[i:][j - 1] in ("+", "-", "*", "/", "=") or j == len(eq) - 1:
          print(f"Found special character: \'{eq[i + 1 :][:j]}\'")
          gl = readGlyph(begWth + eq[i + 1 :][:j])
          render = add2dArrays(render, gl, AbarHt = barHt)
          lastHeight = gl
          i += 1
          break

    else:
      raise Exception(f" Unidentified character: {eq[i]}")
    
    if logging: print2dArray(render, barHt)
      
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
  print(f"Removed empty overhead line [{max(0,count - 1)}]")

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


def add2dArrays(a, b, overlap=-1, relHt=-1, AbarHt=-1, BbarHt=-1, add = 0):
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
      ) + add
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


def print2dArray(arr, bh = None):
  if bh != None:
    H = [[False, False]] * len(arr)
    H[len(H) - 1 - bh] = [True, False]
    arr = add2dArrays(H, arr)
  
  print(f"Dimensions: {len(arr[0])}x{len(arr)}")
  print("--PRERENDER--")
  for y in range(len(arr)):
    for x in range(len(arr[0])):
      print("██" if arr[y][x] else "  ", end="")
    print()
  print("--PRERENDER--")
  
  
equation = r"1+e^{2\pi}-(3x\sqrt{\frac{sin(4)}{5}log_{6}(7)*8}/9)^{10}"
equation = r"1 + e^{2} - (3 * \sqrt{ \frac{sin(4)}{5^{ 2 }} + 8 * log_{6}(7)} / 9)^{ 2 }"
equation = r"\frac{1}{2^{3}}log_{4}(5)"
equation = r"\frac{1}{2}log_{4}(5)"
equation = r"log_{4}(5)"

equation = r"\sqrt{2}{5}"
answer = Evaluator.Evaluate(equation)

r = genRender(equation + "=" + str(answer).replace("-", "_"))
if not logging: print2dArray(r)
