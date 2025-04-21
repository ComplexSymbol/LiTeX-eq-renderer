import Evaluator
import math
import prerendered
#import DictGen

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
  'x': 198,
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
  'comb': 352,
  'perm': 363,
  '=': 374,
  'f': 385,
  '`': 396,
  'rad': 407,
  '^(': 413,
  '^)': 421,
  '^+': 429,
  '^-': 437,
  '^*': 445,
  '^/': 453,
  '^0': 461,
  '^1': 469,
  '^2': 477,
  '^3': 485,
  '^4': 493,
  '^5': 501,
  '^6': 509,
  '^7': 517,
  '^8': 525,
  '^9': 533,
  '^x': 541,
  '^s': 549,
  '^im': 557,
  '^i': 565,
  '^n': 573,
  '^c': 581,
  '^o': 589,
  '^t': 597,
  '^a': 605,
  '^l': 613,
  '^g': 621,
  '^h': 629,
  '^pi': 637,
  '^e': 645,
  '^~': 653,
  '^`': 661,
  '^.': 669,
}
preRenderedGlyphs = {}

lastFinishedBarHt = None
def genRender(eq, exp=False, first = False):
  global lastFinishedBarHt
  i = 0
  begWth = "" if exp == False else "^"
  lastHeight = 0
  barHt = 2 if exp else 4
  render = Render(0, [])
  hang = 0
  eq = eq.replace(" ", "")

  while i < len(eq):
    print(f"Parsing char: {eq[:i] + ' [' + eq[i] + '] ' + eq[i + 1:]} with hang {hang}")

    # Trivial characters
    if eq[i].isdigit() or eq[i].isalpha() or eq[i] in ("+", "-", "*", "/", "=", ".", "~", "`"):
      print(f" Appending digit '{eq[i]}'")
      char = readGlyph(begWth + eq[i])
      render = add2dArrays(render, char, AbarHt=barHt)
      lastHeight = len(char.bitmap)

      del char

    elif eq[i] == "(":
      #print(f" Found parenthesis")
      contents = Evaluator.Between(eq[i:], "(", ")")
      renderedConts = genRender(contents, exp)
      parenHeight = max(0, len(renderedConts.bitmap) - (7 if exp else 10))

      # Opening parenthesis
      render = add2dArrays(
        render,
        readGlyph(begWth + "(", -parenHeight, exp),
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      barHt = max(barHt, lastFinishedBarHt)
      # Contents
      render = add2dArrays(
        render,
        renderedConts,
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      # Closing parenthesis
      render = add2dArrays(
        render,
        readGlyph(begWth + ")", parenHeight, exp),
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      lastHeight = parenHeight + (7 if exp else 10) + hang

      #print(f"  setting i to {len(contents) + 1}")
      i += len(contents) + 1
      del contents, renderedConts, parenHeight

    elif eq[i] == "^" or eq[i] == "_":
      isPwr = eq[i] == "^"
      #print(f"Found exponent/subscript at index {i}")

      contents = Evaluator.Between(eq[i:], "{", "}")
      ln = len(contents)
      contents = genRender(contents, True)

      if isPwr:
        render = add2dArrays(
          render, contents, overlap=3 if exp else 4, relHt=lastHeight
        )
      else:
        render = add2dArrays(render, contents, AbarHt=barHt, BbarHt=len(contents.bitmap) - (2 if exp else 0), add=len(contents.bitmap) - barHt)
        barHt += max(0, len(contents.bitmap) - barHt)

      i += ln + 2
      del isPwr, contents, ln

    elif eq[i] == "\\":
      #print("Found escape sequence")
      esc = None
      # Operator or escape character?
      try:
        esc = Evaluator.Between(eq[i:], "\\", "{")
      except ValueError: pass

      # Escape character (Special Character)
      if esc == None or not esc.isalpha():
        specials = ["pi", "e", 'im', "perm", "comb"]
        tries = [eq[i + 1:].startswith(ch) for ch in specials]

        # None of the accepted special characters were found
        if not any(tries):
          raise ValueError(f"Unidentified special character starting at: {eq[i:]}")

        #print(f"Found special character: {specials[tries.index(True)]}")

        # Generate render for character, then append it to the render and increment i
        char = readGlyph(begWth + specials[tries.index(True)])
        render = add2dArrays(render, char, AbarHt = barHt)
        lastHeight = len(char)
        i += len(specials[tries.index(True)])

        del specials, tries, char

      # Found fraction!
      elif esc == "frac":
        # Numerator & Denominator for fraction.
        num = Evaluator.Between(eq[i:], "{", "}")
        den = Evaluator.Between(eq[i + len(num) + 7:], "{", "}")
        #print(f"Setting i to: {i + len(num) + len(den) + 8}" )
        i += len(num) + len(den) + 8

        num = genRender(num, True)
        den = genRender(den, True)

        fraction = [[False] * (max(len(num[0]), len(den[0])) + 1 + (max(len(num[0]), len(den[0])) % 2)) for _ in range(len(num) + len(den) + 2)]
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
        radical = merge2dArrays(radical, n, 0, (len(radical) - len(n)) // 2)
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

  #print("Removing overhead...")
  #count = 0
  #while True:
  #  if render.bitmap[0] == 0:
  #    del render.bitmap[0]
  #    count += 1
  #    continue
  #  break
  #render.bitmap.insert(0, 0)
  #print(f"Removed {max(0,count - 1)} empty overhead lines")

  print(f"Finished parsing {eq}")

  lastFinishedBarHt = None if first else barHt
  return render

def readGlyph(g, resizeParenBy = 0, exponent = False):
  try:
    glyph = prerendered.prerenderedGlyphs[g] 
    glyph = Render(glyph[0], glyph[1]) # See prerendered.py {Tuple: (w, bmap)}

    if resizeParenBy != 0:
      for _ in range(abs(resizeParenBy)):
        glyph.bitmap.insert(4, (2 if exponent else 4) if resizeParenBy < 0 else 1)

    return glyph

  except KeyError:
    raise Exception(f"Glyph not found '{g}'")

class Render:
  def __init__(self, w, bmap = None,convert = False):
    if convert:
      newBmap = []
      for row in bmap:
        rowInt = 0
        for bit in row:
          rowInt = (rowInt << 1) | (bit & 0b1)
        newBmap.append(rowInt)
      
      bmap = newBmap

    self.bitmap = bmap or []
    self.width = w
    
def testPrint(render, prettyPrint=False):
  if not isinstance(render, Render):
    raise TypeError(f"render ({render}) is not of type Render and cannot be testPrinted")

  if prettyPrint:
    for i, row in enumerate(render.bitmap):
      print(('0' * (render.width - max(1, row.bit_length())) + f"{row:b}").replace("1", "██").replace("0", "{}"))

  else:
    print("[", end="")
    for i, row in enumerate(render.bitmap):
      print("0b" + ('0' * (render.width - max(1, row.bit_length())) + f"{row:b}"), end="," if i < len(render.bitmap) - 1 else "")
    print("]")


def readGlyphForPrerender(g):
  with open("lib/glyphs.txt", "r") as glyphs:
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

    return glyph

  raise Exception(f"Glyph not found '{g}'")

def prerenderGlyphs():
  for key, value in glyphDict.items():
    with open("lib/glyphs.txt", "r") as glyphs:
      glyphs = glyphs.readlines()
      line = glyphs[value].replace("\n", "").replace(key, "", 1).replace(":", "")

      width = 6 if len(line) == 0 else int(line.rpartition("x")[0])
      height = 10 if len(line) == 0 else int(line.rpartition("x")[2])
      
      glyph = [[False] * width] * height

      for y in range(height):
        line = [
          True if digit == "1" else False
          for digit in bin(int(glyphs[value + y + 1]))[2:]
        ]
        line = [False] * (width - len(line)) + line
        glyph[y] = line

    print(f"\"{key}\": ({width}, {Render(width, glyph, True).bitmap}),")

def mergeRenders(a, b, x, y):
  #print("    MERGING")
  #testPrint(a, True)
  #print("    AND")
  #testPrint(b, True)
  
  y = len(a.bitmap) - y
  for h in range(y + 1 - len(b.bitmap), min(len(a.bitmap), y + 1)):
    a.bitmap[h] |= b.bitmap[h - y] << (a.width - x - b.width)

  #print("    RESULT:")
  #testPrint(a, True)

  return a

def add2dArrays(a, b, overlap=-1, relHt=-1, AbarHt=-1, BbarHt=-1, add = 0):
  #print("a: ")
  #testPrint(a, True)
  #print("b: ")
  #testPrint(b, True)

  if relHt == -1:
    relHt = len(a.bitmap)
  if AbarHt == -1:
    AbarHt = (len(a.bitmap) // 2) - 1
  if BbarHt == -1:
    BbarHt = (len(b.bitmap) // 2) - 1
  diff = (AbarHt - BbarHt) if overlap == -1 else 0

  print(f"Add2dArrays ARGS: overlap: {overlap}, relHt: {relHt}, AbarHt: {AbarHt}, BbarHt: {BbarHt}, diff: {diff}")

  # IF NOT OVERLAP: 
  #   height of a 
  #   PLUS how much taller b's contents are when barHt is aligned 
  #   PLUS how much lower b's contents are when barHt is aligned 
  #   PLUS add
  # ELSE:
  # MAX(height of a, relative height PLUS height of b MINUS overlap)
  newHeight = ((len(a.bitmap) + max((AbarHt - len(a.bitmap)) - (BbarHt - len(b.bitmap)), 0) + max(BbarHt - BbarHt, 0))
                if overlap == -1
                else max(len(a.bitmap), relHt + len(b.bitmap) - overlap)
              ) if add == 0 else len(a.bitmap) + add
  newArray = Render(a.width + b.width, [0 for _ in range(newHeight)])
  newArray = mergeRenders(newArray, a, 0, add if diff < 0 else 0)
  newArray = mergeRenders(
    newArray,
    b,
    a.width,
    (diff if diff > 0 else 0) if overlap == -1 else (relHt - overlap),
  )

  #print("result of add: ")
  #testPrint(newArray, True)

  return newArray