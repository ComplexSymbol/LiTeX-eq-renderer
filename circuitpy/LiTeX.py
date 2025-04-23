import Evaluator
import math
import prerendered
#import DictGen

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
    #print(f"Parsing char: {eq[:i] + ' [' + eq[i] + '] ' + eq[i + 1:]} with hang {hang}")

    # Trivial characters
    if eq[i].isdigit() or eq[i].isalpha() or eq[i] in ("+", "-", "*", "/", "=", ".", "~", "`"):
      #print(f" Appending digit '{eq[i]}'")
      char = readGlyph(begWth + eq[i])
      render = addRenders(render, char, AbarHt=barHt)
      lastHeight = len(char.bitmap)

      del char

    elif eq[i] == "(" or eq[i] == "[":
      #print(f" Found parenthesis")
      pair = ("(", ")") if eq[i] == "(" else ("[", "]")
      contents = Evaluator.Between(eq[i:], pair[0], pair[1])
      renderedConts = genRender(contents, exp)
      parenHeight = max(0, len(renderedConts.bitmap) - (7 if exp else 10))

      # Opening parenthesis
      render = addRenders(
        render,
        readGlyph(begWth + pair[0], -parenHeight, exp, pair[0] == "["),
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      
      barHt = max(barHt, lastFinishedBarHt)
      # Contents
      render = addRenders(
        render,
        renderedConts,
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      # Closing parenthesis
      render = addRenders(
        render,
        readGlyph(begWth + pair[1], parenHeight, exp, pair[0] == "["),
        AbarHt=barHt,
        BbarHt=lastFinishedBarHt,
      )
      lastHeight = parenHeight + (7 if exp else 10) + hang

      #print(f"  setting i to {len(contents) + 1}")
      i += len(contents) + 1
      del contents, renderedConts, parenHeight, pair

    elif eq[i] == "^" or eq[i] == "_":
      isPwr = eq[i] == "^"
      #print(f"Found exponent/subscript at index {i}")

      contents = Evaluator.Between(eq[i:], "{", "}")
      ln = len(contents)
      contents = genRender(contents, True)

      if isPwr:
        render = addRenders(
          render, contents, overlap=3 if exp else 4, relHt=lastHeight + hang
        )
      else:
        contentLen = len(contents.bitmap)
        render = addRenders(render, contents, AbarHt=barHt, BbarHt=contentLen - (2 if exp else 0))
        barHt += max(0, contentLen) - barHt - (2 if exp else 0)
        hang += contentLen - 4
        del contentLen

      i += ln + 2
      del isPwr, contents,

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
        render = addRenders(render, char, AbarHt = barHt)
        lastHeight = len(char.bitmap)
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
        denLen = len(den.bitmap)

        fraction = Render(max(num.width, den.width) + 2,
                          [0 for _ in range(len(num.bitmap) + denLen + 2)])
        fraction = mergeRenders(
          fraction,
          num,
          (fraction.width // 2) - (num.width // 2),
          denLen + 2,
        )
        fraction = mergeRenders(
          fraction,
          den,
          (fraction.width // 2) - (den.width // 2),
          0,
        )
        fraction = mergeRenders(
          fraction,
          Render(fraction.width - 1, [(0b1 << fraction.width - 1) - 1]),
          1,
          denLen + 1,
        )
        barHt = max(barHt, denLen) + hang
        render = addRenders(
          render, fraction, AbarHt=barHt, BbarHt=denLen
        )
        lastHeight = len(fraction.bitmap) + hang

        del num, den, fraction, denLen

      elif esc == "sqrt":
        # Nth root
        n = Evaluator.Between(eq[i:], "{", "}")
        radicand = Evaluator.Between(eq[i + len(n) + 7:], "{", "}")
        i += len(n) + len(radicand) + 8

        n = genRender(n, True) if n != "2" else Render(2, [0])
        radicand = genRender(radicand, exp)
        radicandHeight = len(radicand.bitmap)
        stem = Render(2, [0b00] + 
                        ([0b01] * ((radicandHeight) // 2)) + 
                        ([0b10] * ((radicandHeight - (radicandHeight + 1) // 2) - 3))
                     )

        radical = Render(radicand.width + n.width + 5, [0 for _ in range(2 + radicandHeight + max(0, len(n.bitmap) + 2 - radicandHeight))])
        radical = mergeRenders(radical, n, 0, 4)
        radical = mergeRenders(radical, readGlyph("rad"), n.width - 2, 0)
        radical = mergeRenders(radical, stem, n.width + 1, 4)
        radical = mergeRenders(radical, radicand, n.width + 3, 0)
        radical = mergeRenders(radical, Render(radicand.width + 3, [(0b1 << (radicand.width + 3)) - 1]), n.width + 2, radicandHeight + 1)
        radical = mergeRenders(radical, Render(1, [0b1, 0b1]), radicand.width + n.width + 4, radicandHeight - 1)

        render = addRenders(render, radical, AbarHt = barHt, BbarHt = lastFinishedBarHt)
        barHt = max(barHt, lastFinishedBarHt) + hang
        lastHeight = len(radical.bitmap) + hang

        del n, radicand, stem, radical

      del esc

    else:
      raise Exception(f" Unidentified character: {eq[i]}")

    i += 1

  #print(f"Finished parsing {eq}")

  lastFinishedBarHt = None if first else barHt
  return render

def readGlyph(g, resizeBy = 0, exponent = False, absVal = False):
  try:
    if exponent and abs(resizeBy) > 10:
      exponent = False
      g = g[1:]
      
    glyph = prerendered.prerenderedGlyphs[g]
    glyph = Render(glyph[0], glyph[1][:]) # See prerendered.py {Tuple: (w, bmap)}

    if resizeBy != 0:
      for _ in range(abs(resizeBy)):
        glyph.bitmap.insert(4, 1 if absVal else ((2 if exponent else 4) if resizeBy < 0 else 1))

    return glyph

  except KeyError:
    raise Exception(f"Glyph not found '{g}'")

class Render:
  def __init__(self, w, bmap = None, convert = False):
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

printGlyphs = {
  0b0000: "  ",
  0b0001: " ▄",
  0b0010: "▄ ",
  0b0011: "▄▄",
  0b0100: " ▀",
  0b0101: " █",
  0b0110: "▄▀",
  0b0111: "▄█",
  0b1000: "▀ ",
  0b1001: "▀▄",
  0b1010: "█ ",
  0b1011: "█▄",
  0b1100: "▀▀",
  0b1101: "▀█",
  0b1110: "█▀",
  0b1111: "██"
}  
def testPrint(render, prettyPrint=False):
  if not isinstance(render, Render):
    raise TypeError(f"render ({render}) is not of type Render and cannot be testPrinted")

  if prettyPrint:
    if len(render.bitmap) % 2 != 0:
      render.bitmap.append([0])
    if render.width % 2 != 0:
      render.width += 1
    
    for y in range(0, len(render.bitmap), 2):
      for x in range(0, render.width, 2):
        key = (
          (0b1000 if (render.bitmap[y] >> (render.width - x - 1)) & 1 else 0) |
          (0b0100 if (render.bitmap[y] >> (render.width - x - 2)) & 1 else 0) |
          (0b0010 if (render.bitmap[y + 1] >> (render.width - x - 1)) & 1 else 0) |
          (0b0001 if (render.bitmap[y + 1] >> (render.width - x - 2)) & 1 else 0)
        )
        print(printGlyphs[key], end="")
      print()

  else:
    print("[", end="")
    for i, row in enumerate(render.bitmap):
      print("0b" + ('0' * (render.width - max(1, row.bit_length())) + f"{row:b}"), end="," if i < len(render.bitmap) - 1 else "")
    print("]")


def mergeRenders(a, b, x, y):
  y = len(a.bitmap) - y
  
  for h in range(y + 1 - len(b.bitmap), min(len(a.bitmap), y + 1)):
    a.bitmap[h] |= b.bitmap[h - y] << max(0, a.width - x - b.width)

  return a

def addRenders(a, b, overlap=-1, relHt=-1, AbarHt=-1, BbarHt=-1):
  heightA = len(a.bitmap)
  heightB = len(b.bitmap)
  if relHt == -1:
    relHt = heightA
  if AbarHt == -1:
    AbarHt = (heightA // 2) - 1
  if BbarHt == -1:
    BbarHt = (heightB // 2) - 1
  diff = (AbarHt - BbarHt) if overlap == -1 else 0

  #print(f"addRenders ARGS: overlap: {overlap}, relHt: {relHt}, AbarHt: {AbarHt}, BbarHt: {BbarHt}, diff: {diff}")

  newHeight = ((heightA + max((AbarHt - heightA) - (BbarHt - heightB), 0) + max(BbarHt - AbarHt, 0))
              if overlap == -1
              else max(heightA, relHt + heightB - overlap))
  newArray = Render(a.width + b.width, [0 for _ in range(newHeight)])
  newArray = mergeRenders(newArray, a, 0, (-diff if diff < 0 else 0))
  newArray = mergeRenders(
    newArray,
    b,
    a.width,
    (diff if diff > 0 else 0) if overlap == -1 else (relHt - overlap),
  )

  return newArray