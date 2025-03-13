# Evaluates an expression in LiTeX format
def Evaluate(eq):
  print("Evaluating \'{eq}\'")
  
  # Evaluate until finished
  while (True):
    try:
      # Is our equation just a number?
      ans = float(eq)
      return ans;
    
    # If not, continue evaluating
    except ValueError:
      print(f"Equation \'{eq}\' needs further evaluation")
      eq = EvalIteration(eq);

# One iteration of evaluation
# Follows strict PEDMAS
def EvalIteration(eq):
  # P - Parenthesis
  if "(" in eq:
    contents = Between(eq, "(", ")")
    eq = eq.replace(f"({contents})", Evaluate(contents))
    return eq
  
  # E - Exponents
  elif "^" in eq:
    exp = Between(eq[eq.index("^"):], "{", "}")
    base = "0"
    
    i = 0
    while not eq[:eq.index("^")][i:].isdecimal(): i += 1
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
    while not before[i:].isdecimal(): i += 1
    first = before[i:]
    
    i = 0
    after = eq[eq.index(curOp):]
    while not after[eq.index(curOp) + i:].isdecimal(): i += 1
    second = after[eq.index(curOp) + i:]
    
    print(f"  Found operator \'{curOp}\' with first \'{first}\' and second \'{second}\'")
    print(f"  Result: {operate[curOp](first, second)}")
    eq = eq.replace(f"{first}{curOp}{second}", str(operate[curOp](first, second)))
    return eq
    
# Finds string subset between char1 and char2, with nesting support
def Between(string, char1, char2):
  for i in range(len(string)):
    if string[i] == char2 and (string[:i].count(char1) == string[:i + 1].count(char2)):
      return string[string.index(char1) + 1 : i]
  
  raise Exception("Something broke!")