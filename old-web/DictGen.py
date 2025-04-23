# Generate dictionary for glyphs
print("glyphDict = {")
with open("glyphs.txt") as glyphs:
  glyphs = glyphs.readlines()
  for dictEnt in [(f"  '{line.rpartition("x")[0][:-1]}': {indx}," if "x" in line
              else f"  '{line[:-2]}': {indx},") for indx, line in enumerate(glyphs) if line.endswith(":\n")]:
    print(dictEnt)
print("}")
