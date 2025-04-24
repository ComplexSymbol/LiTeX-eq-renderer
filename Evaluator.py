import math
import cmath

trigs = {
  'sin': lambda x: cmath.sin(x) if isinstance(x, complex) else math.sin(x),
  'cos': lambda x: cmath.cos(x) if isinstance(x, complex) else math.cos(x),
  'tan': lambda x: cmath.sin(x) / cmath.cos(x) if isinstance(x, complex) else math.tan(x),
  'csc': lambda x: 1 / (cmath.sin(x) if isinstance(x, complex) else math.sin(x)),
  'sec': lambda x: 1 / (cmath.cos(x) if isinstance(x, complex) else math.cos(x)),
  'cot': lambda x: 1 / (cmath.tan(x) if isinstance(x, complex) else math.tan(x)),
  'asin': lambda x: cmath.asin(x) if isinstance(x, complex) else math.asin(x),
  'acos': lambda x: cmath.acos(x) if isinstance(x, complex) else math.acos(x),
  'atan': lambda x: 1 if isinstance(x, complex) else math.atan(x)
}

operate = {
  0: lambda x, y: toFloat(x) / toFloat(y),
  1: lambda x, y: toFloat(x) * toFloat(y),
  2: lambda x, y: toFloat(x) + toFloat(y),
  3: lambda x, y: toFloat(x) - toFloat(y)
}

# Follows strict PEDMAS
def Evaluate(eq, solve = False, repl = False, guess = 10, shouldGuessImag = False):  
  if isFloat(eq):
    return toFloat(eq)
    
  if repl:
    #print(f"Standardizing eq: '{eq}'")

    if '`' in eq:
      raise ValueError("Incomplete expression")

    eq = eq.replace("~", "-").replace(r"\im", "j")
  
    eq = impMult(eq)
  
    # Change constants into numbers
    eq = eq.replace("\\pi", f"{math.pi}").replace("\\e", f"{math.e}")
    #print(f"   Eq is {eq} after replacing constants")

  eq = impMult(eq)
    
  if solve:
    return NewtonMethod(eq, guess, 8, shouldGuessImag)
  
  #print(f"Evaluating \'{eq}\'")
  
  # P - Parenthetical function (trig)
  while True:
    found = [(eq.find(func), func) for func in ["sin", "cos", "tan", "sec", "csc", "cot"] if func in eq]

    if not found:
      break

    pos, func = min(found, key=lambda x: x[0])  # Get first match in string

    is_inverse = False
    if eq[pos + 3:pos + 8] == "^{-1}":
      is_inverse = True
      func = "a" + func
    
    contents = Between(eq, eq.index(func[1:] if is_inverse else func) + (8 if is_inverse else 3), "(", ")")

    #print(f"  Found trig function {func} with contents {contents}")
    eq = eq.replace(f"{found[0][1] + "^{-1}" if is_inverse else func}({contents})", 
                    str(trigs[func](Evaluate(contents))))

  # P - Parenthetical function (log)  
  while "log" in eq: 
    location = eq.index("log")
    base = Between(eq, location + 3, "{", "}")
    contents = Between(eq, location + len(base) + 6, "(", ")")
    #print(f"  Found logarithm with base {base} and contents {contents}")
    
    eq = eq.replace("log_{"+base+"}" + f"({contents})", 
                    str(cmath.log(Evaluate(contents), Evaluate(base))))
  
  # P - Parenthesis
  while "(" in eq or "[" in eq:
    pair = ("(", ")") if "(" in eq else ("[", "]")
    contents = Between(eq, 0, pair[0], pair[1])
    #print(f"  Found {'parenthesis' if pair[0] == '(' else 'absolute value'} with contents{contents}")
    
    sign = 1
    if eq[eq.index(pair[0]) - 1] == "-":
      sign = -1
      eq = eq[:eq.index(pair[0]) - 1] + eq[eq.index(pair[0]):]

    evCont = Evaluate(contents)
    evCont = abs(evCont) if pair[0] == "[" else evCont
    eq = eq.replace(f"{pair[0]}{contents}{pair[1]}", 
                    str(sign * evCont).replace(pair[0], "").replace(pair[1], ""))

  # E - Exponents
  while "^" in eq:
    exp = Between(eq, eq.index("^"), "{", "}")
    base = None
    
    i = 0
    base = eq[:eq.index("^")]
    while not isFloat(base): 
      i += 1
      base = eq[:eq.index("^")][i:]

    if eq[eq.index(base) - 1] == "+":
      base = base[1:]
    
    #print(f"  Found exponent with base {base} and exponent {exp}")
    eq = eq.replace(base + "^{"+exp+"}",
                    str(toFloat(pow(toFloat(base), Evaluate(exp)))))

  # E - Exponents (square root)
  while r"sqrt" in eq:
    start = eq.index(r"\sqrt") + 5
    nthroot = Between(eq, start, "{", "}")
    contents = Between(eq, start + len(nthroot) + 2, "{", "}")
    #print(f"  Found a {nthroot} degree radical containing {contents}")
    
    eq = eq.replace(r"\sqrt{"+nthroot+"}" + "{"+contents+"}", 
                    str(toFloat(pow(Evaluate(contents), 1 / Evaluate(nthroot)))))

  # D - Division (Fractions have priority)
  while r"frac" in eq:
    start = eq.index(r"\frac") + 5
    numer = Between(eq, start, "{", "}")
    denom = Between(eq, start + len(numer) + 2, "{", "}")
    #print(f"  Found a fraction with numerator {numer} and denominator {denom}")
    
    eq = eq.replace(r"\frac{"+numer+"}" + "{"+denom+"}", 
                    str(toFloat(Evaluate(numer) / Evaluate(denom))))

  # Reevaluate parenthesis because complex numbers
  while "(" in eq:
    contents = Between(eq, 0, "(", ")")
    #print(f"  Found parenthesis with contents{contents}")
    
    sign = 1
    if eq[eq.index("(" + contents) - 1] == "-":
      sign = -1
      eq = eq[:eq.index("(" + contents) - 1] + eq[eq.index("(" + contents):]

    eq = eq.replace(f"({contents})", 
                    str(sign * Evaluate(contents)).replace("(", "").replace(")", ""), 1)
  
  # Permutations and Combinations
  while r"\perm" in eq or r"\comb" in eq:
    eq = eq.replace("*\\perm*", "\\perm").replace("*\\comb*", "\\comb")
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
  eq = eq.replace("+-", "-")
  replaced = False
  doNotCheck = False
  curOp = 0
  progress = max(0, eq.find("/"))
  #print(f"  Finding operations in {eq}")
  while doNotCheck or (set(eq) & frozenset("/*+-") and not isFloat(eq)):
    opStr = ("/", "*", "+", "-")[curOp]
    
    if not opStr in eq[progress:]:
      curOp += 1 if curOp < 3 else -1
      progress = 0
      doNotCheck = True
      continue
        
    progress = eq.index(opStr, progress)
    if eq[progress - 1] == "e":
      doNotCheck = True
      continue
    
    if not replaced and " " in eq and curOp == 3:
      eq = eq.replace(" ", "")
      progress = 0
      replaced = True
      doNotCheck = True
      continue

    doNotCheck = False
    
    i = 0
    while not isFloat(eq[:progress][i:]): i += 1
    first = eq[:progress][i:]
    
    i = len(eq) - progress
    while not isFloat(eq[progress + 1:][:i]): i -= 1
    second = eq[progress + 1:][:i]

    repl = str(operate[curOp](first, second))
    if repl[-2] == "j":
      repl = repl[1:][:-1]

    #print(f"  Found operator \'{eq[progress]}\' with first \'{first}\' and second \'{second}\'. Result: {repl}")
    eq = eq.replace(f"{first}{eq[progress]}{second}", 
                    repl)
    #print(f"setting progress from {progress} to {progress - len(first) + len(repl) - 1}")
    progress = progress - len(first) + len(repl) - 1
    #print(eq)

  ans = toFloat(eq)
  #print(f"  Finished evaluating; result: {ans}")
  return complex(round(complex(ans).real, 15), round(complex(ans).imag, 15)) if repl else ans

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
    if ((eq[i].isdigit() and eq[i + 1] == "\\") or # 5\pi
        (eq[i].isdigit() and eq[i + 1] == "(") or # 2(3 ...
        (eq[i].isdigit() and eq[i + 1].isalpha() and eq[i + 1] != "e" and eq[i + 1] != "j") or # 9sin(... but not 3e or 3j
        (eq[i].isalpha() and eq[i + 1].isdigit()) or # \pi3...
        (eq[i].isalpha() and eq[i + 1] == "\\") or # \pi\e...
        (eq[i] == "j" and eq[i + 1].isalpha()) or # jsin(...
        (eq[i] == ")" and eq[i + 1] == "\\") or # ...4)\pi
        (eq[i] == ")" and eq[i + 1] == "(") or # ...3)(6...
        (eq[i] == ")" and eq[i + 1].isdigit()) or # ...)7
        (eq[i] == ")" and eq[i + 1].isalpha()) or # ...)x...
        (eq[i] == "}" and eq[i + 1].isdigit())): # ...2}7
      eq = eq[:i + 1] + "*" + eq[i + 1:] # Insert multiplication
    i += 1
  return eq

# Finds string subset between char1 and char2, with nesting support
def Between(string, start, char1, char2):
  char1Indx = 0
  char1Cnt = 0
  char2Cnt = 0
  for i in range(start, len(string)):
    if string[i] == char1:
      if char1Cnt == 0:
        char1Indx = i
      
      char1Cnt += 1
    elif string[i] == char2:
      char2Cnt += 1
      
      if char1Cnt == char2Cnt:
        return string[char1Indx + 1 : i]

  raise ValueError(f"Unable to find contents between {char1} and {char2}")

def isFloat(string):
  if len(string) == 0 or string[0] == "+": return False
  
  try:
    toFloat(string)
    return True

  except ValueError:
    return False
    
def toFloat(string):  
  cmplx = complex(string)

  # Complex or imaginary
  return cmplx if cmplx.imag != 0 else cmplx.real
  
inc = 0.001
def NewtonMethod(eq, guess, accuracy, shouldGuessImag, alter = 1, epsilon = 0.00001, maxIter = 40):
  if shouldGuessImag:
    guess = guess + 1j

  for i in range(maxIter):
    if i == maxIter - 1:
      raise ValueError(f"No root found under {maxIter} iterations")
    
    inputEQ = eq.replace("x", str(guess))
    funcAtGuess = Evaluate(inputEQ)
    if abs(funcAtGuess.real + funcAtGuess.imag) < 2 * math.pow(10, -accuracy - 1):
      break
    
    derivAtGuess = (funcAtGuess - Evaluate(eq.replace("x", str(guess - inc)))) / inc
    if abs(derivAtGuess) < epsilon:
      raise ValueError(f"Function too flat... Possible asymptote. Try another guess. {derivAtGuess}")
    
    testGuess = (guess * derivAtGuess - funcAtGuess) / derivAtGuess
    if not shouldGuessImag and Evaluate(eq.replace("x", str(testGuess))).imag != 0:
      doubleDerivAtGuess = (derivAtGuess - ((funcAtGuess - Evaluate(eq.replace("x", str(guess - inc - inc)))) / inc)) / inc
      #print(f"{'Decrimenting' if doubleDerivAtGuess.real < 0 else 'Incrementing'} guess {guess} by {alter}")
      guess += -alter if doubleDerivAtGuess.real < 0 else alter
      continue
    
    guess = testGuess
    #print(f"New Guess: {guess}")
    
  
  return complex(round(complex(guess).real, accuracy), round(complex(guess).imag, accuracy))



