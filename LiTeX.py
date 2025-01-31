def genRender(eq, exp = False):
  i = 0
  mode = ""
  render = [[]]
  begWth = "" if exp == False else "^"
  lastHeight = 0

  while i < len(eq):
    print(f"Parsing char: \'{eq[i]}\' at index {i} of {eq}")
    
    if eq[i].isdigit() or eq[i] in ("+", "-", "*", "/"):
      print(f"  Appending digit \'{eq[i]}\'")
      render = add2dArrays(render, readGlyph(begWth + eq[i]))
      lastHeight = len(readGlyph(begWth + eq[i]))

    elif eq[i] == "(":
      print(f"  Found parenthesis")
      for j in range(1, len(eq[i:]) + 1):
        if eq[i:][:j].count("(") == eq[i:][:j].count(")"):
          print(f"    Found end of parenthesis at index {i + j} [contents: {eq[i:][:j]}]")
          print(f"    Recursing contents {eq[i+1:][:j-2]}")
          
          contents = genRender(eq[i+1:][:j-2], exp)
          print(f"Adding {len(contents) - 10} to paren size")
          
          render = add2dArrays(render, readGlyph(begWth + "(", -(len(contents) - 10)))
          render = add2dArrays(render, contents)
          render = add2dArrays(render, readGlyph(begWth + ")", len(contents) - 10))
          lastHeight = len(readGlyph(begWth + ")", len(contents) - 10))
          
          print(f"    Setting index i to {i + j - 1}")
          i += j - 1
          break

        if j == len(eq[i:]):
          raise Exception("Unfinished parenthesis")

    elif eq[i] == "^":
      i += 1
      print(f"Found power at index {i}")
      
      if eq[i] == '{':
        print(f"  Found exponent brace")
        for j in range(1, len(eq[i:]) + 1):
          if eq[i:][:j].count("{") == eq[i:][:j].count("}"):
            print(f"    Found end of exponent brace at index {i + j} [contents: {eq[i:][:j]}]")
            print(f"    Recursing contents {eq[i+1:][:j-2]}")
            
            render = add2dArrays(render, genRender(eq[i+1:][:j-2], True), 4, len(readGlyph(eq[i - 2])))
            lastHeight =  len(readGlyph(eq[i - 2])) + len(genRender(eq[i+1:][:j-2], True)) - 4
            
            print(f"    Setting index i to {i + j - 1}")
            i += j - 1
            break

        if j == len(eq[i:]):
          raise Exception("Unfinished exponential brace")

      elif eq[i].isdigit():
        for j in range(0, len(eq[i:])):
          if (eq[i:][j].isalnum()):
            print(f"  Appending power: {eq[i:][j]} at index {i + j}")
            thisExp = readGlyph(begWth + "^" + eq[i:][j])
            render = add2dArrays(render, thisExp, 4, -1 if exp else lastHeight)
            lastHeight = (max(len(render), len(thisExp)) if exp else lastHeight) + len(thisExp) - 4
          else:
            j -= 1
            break
        i += j
          
    i += 1
    if i < len(eq):
      print(f"{' ' * (i + len(str(i)) + 31)}V")

  print(f"Finished parsing {eq}")
  return render


def readGlyph(g, resParen = 0):
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
            True if digit == "1" else False for digit in bin(int(glyphs[i]))[2:]
          ]
          line = [False] * (width - len(line)) + line
          glyph[y] = line
          
        for p in range(abs(resParen)):
          glyph.insert(4, 
            [False, True, False, False]
            if resParen < 0 else 
            [False, False, False, True]
          )
        
        print2dArray(glyph)
        return glyph

  raise Exception(f"Glyph not found '{g}'")


def add2dArrays(a, b, overlap = -1, relHt = -1):
  if relHt == -1:
    relHt = len(a)
  
  newArray = [
    [False] * (len(a[0]) + len(b[0]))
      for _ in range(
        max(len(b), len(a)) if overlap == -1 else (relHt + len(b) - overlap)
      )
    ]
  newArray = merge2dArrays(newArray, a, 0, 0)
  newArray = merge2dArrays(
    newArray, b, len(a[0]), 0 if overlap == -1 else (relHt - overlap)
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
  
print2dArray(genRender("1+(2^3-4)^5*6"))


