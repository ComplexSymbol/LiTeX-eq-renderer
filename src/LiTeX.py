import Evaluator
import math

lastFinishedBarHt = None
logging = False

glyphDict = {
  '(': 0,
  ')': 11,
  '0': 22,
  '1': 33,
  '2': 44,
  '3': 55,
  '4': 66,
  '5': 77,
  '6': 88,
  '7': 99,
  '8': 110,
  '9': 121,
  '+': 132,
  '*': 143,
  '-': 154,
  '~': 165,
  '/': 176,
  '.': 187,
  '': 198,
  's': 209,
  'i': 220,
  'im': 231,
  'n': 242,
  'c': 253,
  'o': 264,
  't': 275,
  'a': 286,
  'l': 297,
  'g': 308,
  'h': 319,
  'pi': 330,
  'e': 341,
  '=': 352,
  'f': 363,
  '`': 374,
  'rad': 385,
  '^(': 391,
  '^)': 399,
  '^+': 407,
  '^-': 415,
  '^*': 423,
  '^/': 431,
  '^0': 439,
  '^1': 447,
  '^2': 455,
  '^3': 463,
  '^4': 471,
  '^5': 479,
  '^6': 487,
  '^7': 495,
  '^8': 503,
  '^9': 511,
  '^x': 519,
  '^s': 527,
  '^im': 535,
  '^n': 543,
  '^c': 551,
  '^o': 559,
  '^t': 567,
  '^a': 575,
  '^l': 583,
  '^g': 591,
  '^h': 599,
  '^pi': 607,
  '^e': 615,
  '^~': 623,
  '^`': 631,
}

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
    
    if eq[i].isdigit() or eq[i].isalpha() or eq[i] in ("+", "-", "*", "/", "=", ".", "~", "`"):
      print(f" Appending digit '{eq[i]}'")
      char = readGlyph(begWth + eq[i])
      render = add2dArrays(render, char, AbarHt=barHt)
      lastHeight = len(char)
      
      del char
  
    elif eq[i] == "(":
      print(f" Found parenthesis")
      contents = Evaluator.Between(eq[i:], "(", ")")
      renderedConts = genRender(contents, exp)
      parenHeight = max(0, len(renderedConts) - (7 if exp else 10))
      
      
      render = add2dArrays(
        render,
        readGlyph(begWth + "(", -parenHeight, exp),
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      print2dArray(render)
      barHt = max(barHt, lastFinishedBarHt)
      render = add2dArrays(
        render,
        renderedConts,
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      render = add2dArrays(
        render,
        readGlyph(begWth + ")", parenHeight, exp),
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      lastHeight = parenHeight + (7 if exp else 10) + hang
      
      print(f"  setting i to {len(contents) + 1}")
      i += len(contents) + 1
      
      del contents, renderedConts, parenHeight
    
    elif eq[i] == "^" or eq[i] == "_":
      isPwr = eq[i] == "^"
      print(f"Found exponent/subscript at index {i}")
      
      contents = Evaluator.Between(eq[i:], "{", "}")
      ln = len(contents)
      contents = genRender(contents, True)
      
      if isPwr:
        render = add2dArrays(
          render, contents, overlap=3 if exp else 4, relHt=lastHeight
        )
      else:
        render = add2dArrays(render, contents, AbarHt=barHt, BbarHt=len(contents) - (2 if exp else 0), add = len(contents) - barHt)
        barHt += abs(min(barHt - len(contents), 0))
      
      i += ln + 2
      
      del isPwr, contents, ln
    
    elif eq[i] == "\\":
      print("Found escape sequence")
      esc = None
      # Operator or escape character?
      try:
        esc = Evaluator.Between(eq[i:], "\\", "{")
      except ValueError: pass
    
      # Escape character (Special Character)
      if esc == None or not esc.isalpha():
        specials = ["pi", "e", 'im']
        tries = [eq[i + 1:].startswith(ch) for ch in specials]
        
        # None of the accepted special characters were found
        if not any(tries):
          raise ValueError(f"Unidentified special character starting at: {eq[i:]}")
        
        print(f"Found special character: {specials[tries.index(True)]}")
        
        # Generate render for character, then append it to the render and increment i
        char = readGlyph(begWth + specials[tries.index(True)])
        render = add2dArrays(render, char, AbarHt = barHt)
        lastHeight = len(char)
        i += len(specials[tries.index(True)])
        
        del specials, tries, char
      
      # Since it's not an escape character, it must be a function
      elif esc == "frac":
        # Numerator & Denominator for fraction.
        num = Evaluator.Between(eq[i:], "{", "}")
        den = Evaluator.Between(eq[i + len(num) + 7:], "{", "}")
        print(f"Setting i to: {i + len(num) + len(den) + 8}" )
        i += len(num) + len(den) + 8
        
        num = genRender(num, True)
        den = genRender(den, True)

        fraction = [
          [False] * (max(len(num[0]), len(den[0])) + 1 + (max(len(num[0]), len(den[0])) % 2))
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
        
        del num, den, fraction
        
      elif esc == "sqrt":
        # Nth root
        n = Evaluator.Between(eq[i:], "{", "}")
        radicand = Evaluator.Between(eq[i + len(n) + 7:], "{", "}")
        i += len(n) + len(radicand) + 8
        
        n = genRender(n, True) if n != "2" else [[False, False]]
        radicand = genRender(radicand, exp)
        
        stem = [[False, False]] + ([[False, True]] * ((len(radicand) + 1) // 2))
        stem += [[True, False]] * ((len(radicand) - (len(radicand) + 1) // 2) - 4)
        radical = [[False] * (5 + len(radicand[0]) + len(n[0])) for _ in range(max(len(radicand) + 2, len(radicand) + len(n) - 2))]
        radical = merge2dArrays(radical, n, 0, len(radical) - len(n) - (1 if exp else 2))
        radical = merge2dArrays(radical, readGlyph("rad"), len(n[0]) - 2, 0)
        radical = merge2dArrays(radical, stem, len(n[0]) + 1, 4)
        radical = merge2dArrays(radical, radicand, len(n[0]) + 3, 0)
        radical = merge2dArrays(radical, [[True] * (len(radicand[0]) + 3)], len(n[0]) + 2, len(radicand) + 1)
        radical = merge2dArrays(radical, [[True], [True]], len(radicand[0]) + len(n[0]) + 4, len(radicand) - 1)
        
        render = add2dArrays(render, radical, AbarHt = barHt, BbarHt = lastFinishedBarHt)
        barHt = max(barHt, lastFinishedBarHt) + hang
        lastHeight = len(radical) + hang
        
        del n, radicand, stem, radical
      
      del esc

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
  print(f"Removed empty overhead line [{max(0,count - 1)}]")

  print(f"Finished parsing {eq}")
  lastFinishedBarHt = barHt
  return render


def readGlyph(g, resParen = 0, exp = False):
  with open("glyphs.txt", "r") as glyphs:
    glyphs = glyphs.readlines()
    line = glyphs[glyphDict[g]].replace("\n", "").replace(g, "", 1).replace(":", "")

    width = 6 if len(line) == 0 else int(line.rpartition("x")[0])
    height = 10 if len(line) == 0 else int(line.rpartition("x")[2])
    
    glyph = [[False] * width] * height

    for y in range(height):
      line = [
        True if digit == "1" else False
        for digit in bin(int(glyphs[glyphDict[g] + y + 1]))[2:]
      ]
      line = [False] * (width - len(line)) + line
      glyph[y] = line
      
    for p in range(abs(resParen)):
      print(p)
      glyph.insert(
        4,
        ([False, True, False] if resParen < 0 else [False, False, True]) if exp 
        else ([False, True, False, False]
          if resParen < 0
          else [False, False, False, True]
          )
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

  newArray = [[False] * (len(a[0]) + len(b[0]))] * (
    max(
      max(len(a), len(b)) + ((len(b) - BbarHt - 1) - (len(a) - AbarHt - 1)),
      len(a),
      len(b),
    ) + add
    if overlap == -1
    else max(len(a), relHt + len(b) - overlap)
  )
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
  

equation = r"\frac{\sqrt{90}{\im}-(\sqrt{90}{\im})^{~1}}{2\im}"
equation = r"\frac{\sqrt{90}{\im}-(\sqrt{90}{\im})}{2\im}"
equation = r"\sqrt{90}{\im}"


ans = str(Evaluator.Evaluate(equation, True)).replace("-0", "").replace("-", "~", 1).replace("(", "").replace(")", "").replace("11j", "111j").replace("1j", "j").replace("+0j", "").replace("j", r"\im")
renderANS = genRender("=" + ("0" if ans == r"0\im" else ans))
renderEQ = genRender(equation)

print2dArray(renderEQ)
print2dArray(renderANS)

# Generate dictionary for glyphs
"""
with open("glyphs.txt") as glyphs:
  glyphs = glyphs.readlines()
  for dictEnt in [(f"  '{line.rpartition("x")[0][:-1]}': {indx}," if "x" in line
              else f"  '{line[:-2]}': {indx},") for indx, line in enumerate(glyphs) if line.endswith(":\n")]:
    print(dictEnt)
"""

