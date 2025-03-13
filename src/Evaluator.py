# Evaluates an expression in LiTeX format
def Evaluate(eq):
  print(f"Evaluating \'{eq}\'")
  
  # Evaluate until finished
  while not isFloat(eq):
    print(f"Equation \'{eq}\' needs further evaluation")
    eq = EvalIteration(eq);
    print(f"Equation is now \'{eq}\' after another iteration")
      
  print(f"Equation \'{eq}\' is done being evaluated")
  
  sign = 1
  if eq[0] == "-":
    sign = -1
    eq = eq[1:]
  
  ans = float(eq)
  return sign * ans;
  
# One iteration of evaluation
# Follows strict PEDMAS
def EvalIteration(eq):
  # P - Parenthesis
  if "(" in eq:
    contents = Between(eq, "(", ")")
    eq = eq.replace(f"({contents})", str(Evaluate(contents)))
    return eq
  
  # E - Exponents
  elif "^" in eq:
    exp = Between(eq[eq.index("^"):], "{", "}")
    base = "0"
    
    i = 0
    while not isFloat(eq[:eq.index("^")][i:]): i += 1
    base = eq[:eq.index("^")][i:]
    
    eq = eq.replace(base + "^{"+exp+"}", str(float(base) ** float(exp)))
    return eq
  
  # D - Division (Fractions have priority)
  elif r"\frac" in eq:
    start = eq.find(r"\frac") + 5
    numer = Between(eq[start:], "{", "}")
    denom = Between(eq[start + len(numer) + 2:], "{", "}")
    
    eq = eq.replace(r"\frac{"+numer+"}" + "{"+denom+"}", str(Evaluate(numer) / Evaluate(denom)))
    return eq
  
  # DMAS - In that order
  elif set(eq) & frozenset("/*+-"):
    curOp = "/" if "/" in eq else (
            "*" if "*" in eq else (
            "+" if "+" in eq else (
            "-" if "-" in eq else (
            None))))

    operate = {'+': lambda x, y: float(x) + float(y),
               '-': lambda x, y: float(x) - float(y),
               '*': lambda x, y: float(x) * float(y),
               '/': lambda x, y: float(x) / float(y)}
    
    i = 0
    before = eq[:eq.index(curOp)]
    while not isFloat(before[i:]): i += 1
    first = before[i:]
    
    after = eq[eq.index(curOp) + 1:]
    i = len(after)
    print(f"'{after[:i]}'")
    while not isFloat(after[:i]):
      print(after[:i])
      i -= 1
    second = after[:i]
    
    print(f"  Found operator \'{curOp}\' with first \'{first}\' and second \'{second}\'")
    print(f"  Result: {operate[curOp](first, second)}")
    eq = eq.replace(f"{first}{curOp}{second}", str(operate[curOp](first, second)))
    return eq
    
# Finds string subset between char1 and char2, with nesting support
def Between(string, char1, char2):
  for i in range(len(string)):
    if string[i] == char2 and (string[:i].count(char1) == string[:i + 1].count(char2)):
      return string[string.index(char1) + 1 : i]
  
  raise Exception(f"Unable to find contents between {char1} and {char2}")
      
def isFloat(string):
  try:
    if string[0] == "-": string = string[1:]
    float(string)
    return True

  except ValueError:
    return False