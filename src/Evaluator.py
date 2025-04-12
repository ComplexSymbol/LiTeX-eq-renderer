import math
import cmath


trigs = {
  'sin': lambda x: cmath.sin(x) if isinstance(x, complex) else math.sin(x),
  'cos': lambda x: cmath.cos(x) if isinstance(x, complex) else math.cos(x),
  'tan': lambda x: cmath.tan(x) if isinstance(x, complex) else math.tan(x),
  'csc': lambda x: 1 / (cmath.sin(x) if isinstance(x, complex) else math.sin(x)),
  'sec': lambda x: 1 / (cmath.cos(x) if isinstance(x, complex) else math.cos(x)),
  'cot': lambda x: 1 / (cmath.tan(x) if isinstance(x, complex) else math.tan(x)),
  'asin': lambda x: cmath.asin(x) if isinstance(x, complex) else math.asin(x),
  'acos': lambda x: cmath.acos(x) if isinstance(x, complex) else math.acos(x),
  'atan': lambda x: cmath.atan(x) if isinstance(x, complex) else math.atan(x)
}

operate = {
  '+': lambda x, y: toFloat(x) + toFloat(y),
  '-': lambda x, y: toFloat(x) - toFloat(y),
  '*': lambda x, y: toFloat(x) * toFloat(y),
  '/': lambda x, y: toFloat(x) / toFloat(y)
}

# Follows strict PEDMAS
def Evaluate(eq, solve = False, replace = False):
  global trigs, operate
  
  if isFloat(eq):
    return toFloat(eq)
  
  print(f"Standardizing eq: '{eq}'")
  
  if replace:
    if '`' in eq:
      raise ValueError("Incomplete expression")

    #eq = eq.replace(" - ", " +-")
    eq = eq.replace("~", "-")
    eq = eq.replace("log-", "log_")
    eq = eq.replace(r"\im", "j")
  
  eq = impMult(eq)
  
  # First, change constants into numbers
  specials = ["pi", "e"]
  values = { 'e': math.e, 
             'pi': math.pi,
           }
  tries = [("\\" + sp) in eq for sp in specials]
  while any(tries):
    eq = eq.replace("\\" + specials[tries.index(True)], 
                    str(values[specials[tries.index(True)]]))
    tries[tries.index(True)] = False
  eq = impMult(eq)
  #print(f"   Eq is {eq} after replacing constants")
  
  eq = eq.replace(r"*\perm*", r"\perm").replace(r"*\comb*", r"\comb")
  
  if solve:
    return NewtonMethod(eq, 10, 5, False)
  
  #print(f"Evaluating \'{eq}\'")
  
  # P - Parenthetical function (trig)
  while any(trigs in eq for trigs in ["sin", "cos", "tan", "sec", "csc", "cot"]):
    func = "sin" if "sin" in eq else (
           "cos" if "cos" in eq else (
           "tan" if "tan" in eq else (
           "csc" if "csc" in eq else (
           "sec" if "sec" in eq else (
           "cot" if "cot" in eq else (
           None))))))
   
    if (eq.index(func + "^{-1}") if func + "^{-1}" in eq else None) == eq.index(func):
      func = "a" + func
    
    contents = Between(eq[eq.index(func[1:] if func[0] == "a" else func) + (8 if func[0] == "a" else 3):], "(", ")")
    
    #print(f"  Found trig function {func} with contents {contents}")
    eq = eq.replace(f"{func[1:] + "^{-1}" if func[0] == "a" else func}({contents})", 
                    str(trigs[func](Evaluate(contents))))

  # P - Parenthetical function (log)  
  while "log" in eq: 
    location = eq.index("log")
    base = Between(eq[location + 3:], "{", "}")
    contents = Between(eq[location + len(base) + 6:], "(", ")")
    #print(f"  Found logarithm with base {base} and contents {contents}")
    
    eq = eq.replace("log_{"+base+"}" + f"({contents})", 
                    str(cmath.log(Evaluate(contents), Evaluate(base))))
  

  # P - Parenthesis
  while "(" in eq:
    contents = Between(eq, "(", ")")
    #print(f"  Found parenthesis with contents{contents}")
    
    sign = 1
    if eq[eq.index("(" + contents) - 1] == "-":
      sign = -1
      eq = eq[:eq.index("(" + contents) - 1] + eq[eq.index("(" + contents):]

    eq = eq.replace(f"({contents})", 
                    str(sign * Evaluate(contents)).replace("(", "").replace(")", ""), 1)

  # E - Exponents
  while "^" in eq:
    exp = Between(eq[eq.index("^"):], "{", "}")
    base = None
    
    i = 0
    base = eq[:eq.index("^")]
    while not isFloat(base) or ("j" in base and any(ch.isdigit() for ch in base)): 
      i += 1
      base = eq[:eq.index("^")][i:]

    if eq[eq.index(base) - 1] == "+":
      base = base[1:]
    
    #print(f"  Found exponent with base {base} and exponent {exp}")
    eq = eq.replace(base + "^{"+exp+"}",
                    str(toFloat(pow(toFloat(base), Evaluate(exp)))))

  # E - Exponents (square root)
  while r"\sqrt" in eq:
    start = eq.find(r"\sqrt") + 5
    nthroot = Between(eq[start:], "{", "}")
    contents = Between(eq[start + len(nthroot) + 2:], "{", "}")
    #print(f"  Found a {nthroot} degree radical containing {contents}")
    
    eq = eq.replace(r"\sqrt{"+nthroot+"}" + "{"+contents+"}", 
                    str(toFloat(pow(Evaluate(contents), 1 / Evaluate(nthroot)))))

  # D - Division (Fractions have priority)
  while r"\frac" in eq:
    start = eq.find(r"\frac") + 5
    numer = Between(eq[start:], "{", "}")
    denom = Between(eq[start + len(numer) + 2:], "{", "}")
    #print(f"  Found a fraction with numerator {numer} and denominator {denom}")
    
    eq = eq.replace(r"\frac{"+numer+"}" + "{"+denom+"}", 
                    str(toFloat(Evaluate(numer) / Evaluate(denom))))

  # Reevaluate parenthesis because complex numbers
  while "(" in eq:
    contents = Between(eq, "(", ")")
    #print(f"  Found parenthesis with contents{contents}")
    
    sign = 1
    if eq[eq.index("(" + contents) - 1] == "-":
      sign = -1
      eq = eq[:eq.index("(" + contents) - 1] + eq[eq.index("(" + contents):]

    eq = eq.replace(f"({contents})", 
                    str(sign * Evaluate(contents)).replace("(", "").replace(")", ""), 1)
  
  # Permutations and Combinations
  while r"\perm" in eq or r"\comb" in eq:
    isComb = r"\comb" in eq
    indx = eq.index(r"\comb" if isComb else r"\perm")
    
    i = 0
    while not isFloat(eq[:indx][i:]):
      i += 1
    n = eq[:indx][i:]
    
    i = len(eq)
    while not isFloat(eq[indx + 5:][:i]):
      i -= 1
    r = eq[indx + 5:][:i]
    
    eq = eq.replace(n + (r"\comb" if isComb else r"\perm") + r,
                    str(math.perm(int(n), int(r)) / (math.factorial(int(r)) if isComb else 1)))
  
  # DMAS - In that order
  skip = 0
  eq = eq.replace(" * ", "*").replace(" + ", "+").replace(" / ", "/")
  while set(eq[skip:]) & frozenset("/*+-") and not isFloat(eq[skip:]):
    if eq[skip:][0] == "-":
      skip += 1
      continue
    
    curOp = "/" if "/" in eq[skip:] else (
            "*" if "*" in eq[skip:] else (
            "-" if "-" in eq[skip:] else (
            "+" if "+" in eq[skip:] else (
            None))))
    
    if curOp == "-":
      if " " in eq[skip:]:
        eq = eq.replace(" ", "")
      if eq[skip:][eq[skip:].index("-") - 1] == "e":
        skip = eq[skip:].index("-") + 1
        continue
    
    eqIndxCurOp = skip + eq[skip:].index(curOp)
    
    before = eq[:eqIndxCurOp]
    i = 0
    while not isFloat(before[i:]): 
      i += 1
    first = before[i:]
    
    after = eq[eqIndxCurOp + 1:]
    i = len(after)
    while not isFloat(after[:i]):
      i -= 1
    second = after[:i]
    
    if isFloat(f"{first}{curOp}{second}"):
      skip = eq[skip:].index(curOp) + 1
      continue
    
    print(f"  Found operator \'{curOp}\' with first \'{first}\' and second \'{second}\'")
    eq = eq.replace(f"{first}{curOp}{second}", 
                    str(toFloat(operate[curOp](first, second))).replace("(", "").replace(")", ""))
    skip = 0

  ans = toFloat(eq)
  print(f"  Finished evaluating; result: {ans}")
  return complex(round(complex(ans).real, 15), round(complex(ans).imag, 15)) if replace else ans

def primeFactors(n):
  i = 2
  factors = []
  while i * i <= n:
    if n % i:
      i += 1
    else:
      n //= i
      factors.append(i)
  if n > 1:
    factors.append(n)
  return factors
  
# Add implicit multiplication
def impMult(eq):
  i = 0
  while i < len(eq) - 1:
    # 3 main causes: num*func, paren*func, paren*paren
    if ((eq[i].isdigit() and eq[i + 1] == "\\") or # 5\pi
        (eq[i].isdigit() and eq[i + 1] == "(") or # 2(3 ...
        (eq[i].isdigit() and eq[i + 1].isalpha() and eq[i + 1] != "e") or # 9sin(... but not 3e
        (eq[i].isalpha() and eq[i + 1].isdigit()) or # \pi3...
        (eq[i].isalpha() and eq[i + 1] == "\\") or # \pi\e, X: (\pi
        (eq[i] == "j" and eq[i + 1].isalpha()) or # jsin(...
        (eq[i] == ")" and eq[i + 1] == "\\") or # ...4)\pi
        (eq[i] == ")" and eq[i + 1] == "(") or # ...3)(6...
        (eq[i] == ")" and eq[i + 1].isdigit()) or # ...)7
        (eq[i] == "}" and eq[i + 1].isdigit())): # ...2}7
      eq = eq[:i + 1] + "*" + eq[i + 1:] # Insert multiplication
    i += 1
  return eq

# Finds string subset between char1 and char2, with nesting support
def Between(string, char1, char2):
  for i in range(len(string)):
    if string[i] == char2 and (string[:i].count(char1) == string[:i + 1].count(char2)):
      return string[string.index(char1) + 1 : i]
  
  raise ValueError(f"Unable to find contents between {char1} and {char2}")
     
def isFloat(string):
  if string[0] == "+" or string[0] == " ": return False
  
  try:
    toFloat(string)
    return True

  except ValueError:
    return False
  
def toFloat(string):
  string = str(string)
  
  # Complex or imaginary
  if "j" in string:
    return complex(string)
  
  else: return float(string)
  
inc = 0.001
def NewtonMethod(eq, guess, accuracy, shouldGuessImag):
  while True:
    inputEQ = eq.replace("x", str(guess))
    funcAtGuess = Evaluate(inputEQ)
    if abs(complex(funcAtGuess).real + complex(funcAtGuess).imag) < 2 * math.pow(10, -accuracy - 1):
      break
    
    derivAtGuess = (funcAtGuess - Evaluate(eq.replace("x", str(guess - inc)))) / inc
    testGuess = (guess * derivAtGuess - funcAtGuess) / derivAtGuess
    if not shouldGuessImag and complex(Evaluate(eq.replace("x", str(testGuess)))).imag != 0:
      print(f"Decrementing guess {guess} by 0.5")
      guess += -0.5 if derivAtGuess.real < 0 else 0.5
      continue
    
    guess = testGuess
    print(f"New Guess: {guess}")
  
  return complex(round(complex(guess).real, accuracy), round(complex(guess).imag, accuracy))
  
    
