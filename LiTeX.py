def genRender(eq):
  i = 0
  mode = ""
  render = [[]]

  while i < len(eq):
    print(f"\nParsing char: \'{eq[i]}\' at index {i} of {eq}")
    
    if eq[i].isdigit() or eq[i] in ("+", "-", "*", "/"):
      print(f"  Appending digit \'{eq[i]}\'")
      render = add2dArrays(render, readGlyph(eq[i]))

    elif eq[i] == "(":
      print(f"  Found parenthesis")
      for j in range(1, len(eq[i:]) + 1):
        if eq[i:][:j].count("(") == eq[i:][:j].count(")"):
          print(f"    Found end of parenthesis at index {i + j} [contents: {eq[i:][:j]}]")
          print(f"    Recursing contents {eq[i:][:j][1:][:-1]}")
          
          render = add2dArrays(render, readGlyph("("))
          render = add2dArrays(render, genRender(eq[i:][:j][1:][:-1]))
          render = add2dArrays(render, readGlyph(")"))
          
          print(f"    Setting index i to {i + j - 1}")
          i += j - 1
          break

        if j == len(eq[i:]):
          raise Exception("Unfinished parenthesis")

    elif eq[i] == "^":
      i += 1
      print(f"Found power at index {i}")
      
      if eq[i] == '{':
        

      elif eq[i].isdigit():
        for j in range(0, len(eq[i:])):
          if (eq[i:][j].isalnum()):
            print(f"  Appending power: {eq[i:][j]} at index {i + j}")
            render = add2dArrays(render, readGlyph("^" + eq[i:][j]), 3, len(readGlyph(eq[i - 2])))
          else:
            j -= 1
            break
        i += j
          
    i += 1
  
  print(f"Finished parsing {eq}")
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

  raise Exception(f"Glyph not found '{g}'")


def add2dArrays(a, b, overlap = -1, relHt = -1):
  if relHt == -1:
    relHt = len(a)
  
  newArray = [
    [0] * (len(a[0]) + len(b[0]))
      for _ in range(
        max(len(b), len(a)) if overlap == -1 else (relHt + len(b) - overlap)
      )
    ]
  newArray = merge2dArrays(newArray, a, 0, 0)
  newArray = merge2dArrays(
    newArray, b, len(a[0]), 0 if overlap == -1 else (relHt - overlap)
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
    print(f"{' ' * (len(str(len(arr))) - len(str(y)))}{y}: {arr[y]}", end=",\n")

  print("--PRERENDER-- **NOT TO SCALE**")
  for y in range(len(arr)):
    for x in range(len(arr[0])):
      print("█" if arr[y][x] == 1 else " ", end="")
    print()
  print("--PRERENDER--")
  
print2dArray(genRender("1+(2^3-4)^5+6^{7^7}"))


