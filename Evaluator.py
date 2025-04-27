import math
import cmath
from time import monotonic_ns

trigs = {
  'sin': lambda x: cmath.sin(x) if isinstance(x, complex) else math.sin(x),
  'cos': lambda x: cmath.cos(x) if isinstance(x, complex) else math.cos(x),
  'tan': lambda x: cmath.sin(x) / cmath.cos(x) if isinstance(x, complex) else math.tan(x),
  'csc': lambda x: 1 / (cmath.sin(x) if isinstance(x, complex) else math.sin(x)),
  'sec': lambda x: 1 / (cmath.cos(x) if isinstance(x, complex) else math.cos(x)),
  'cot': lambda x: 1 / (cmath.tan(x) if isinstance(x, complex) else math.tan(x)),
  'asin': lambda x: cmath.asin(x) if isinstance(x, complex) else math.asin(x),
  'acos': lambda x: cmath.acos(x) if isinstance(x, complex) else math.acos(x),
  'atan': lambda x: cmath.atan(x) if isinstance(x, complex) else math.atan(x)
}

operate = {
  0: lambda x, y: toFloat(x) / toFloat(y),
  1: lambda x, y: toFloat(x) * toFloat(y),
  2: lambda x, y: toFloat(x) + toFloat(y),
  3: lambda x, y: toFloat(x) - toFloat(y)
}

# Follows strict PEDMAS
def Evaluate(eq, solve = False, repl = False, guess = 10, shouldGuessImag = False, head=""):   
  if isFloat(eq):
    return toFloat(eq)
    
  if repl:
    #print(head + f"Standardizing eq: '{eq}'")
    if '`' in eq:
      raise ValueError("Incomplete expression")

    eq = eq.replace("~", "-").replace(r"\im", "j")
  
    eq = impMult(eq)
  
    # Change constants into numbers
    eq = eq.replace("\\pi", f"{math.pi}").replace("\\e", f"{math.e}")
    #print(head + f"   Eq is {eq} after replacing constants")

  eq = impMult(eq)
    
  if solve:
    return NewtonMethod(eq, guess, 8, shouldGuessImag)
  
  #print()
  #print(head + f"Evaluating \'{eq}\'")
  
  # P - Parenthetical function (trig)
  found = None
  while found := [(eq.find(func + "("), func) for func in ["sin", "cos", "tan", "sec", "csc", "cot"] if func in eq]:
    pos, func = min(found, key=lambda x: x[0])  # Get first match in string

    is_inverse = False
    if eq[pos + 3:pos + 8] == "^{-1}":
      is_inverse = True
      func = "a" + func
    
    contents = Between(eq, eq.index(func[1:] if is_inverse else func) + (8 if is_inverse else 3), "(", ")")

    #print(head + f"  Found trig function {func} with contents {contents}")
    eq = eq[:pos] + str(trigs[func](Evaluate(contents, head="  "))) + eq[pos + (10 if is_inverse else 5) + len(contents):]
    #eq = eq.replace(f"{found[0][1] + "^{-1}" if is_inverse else func}({contents})", 
    #                str(trigs[func](Evaluate(contents))))

  # P - Parenthetical function (log)
  loc = None
  while (loc := eq.find("log")) != -1:
    base = Between(eq, loc + 3, "{", "}")
    contents = Between(eq, loc + len(base) + 6, "(", ")")
    #print(head + f"  Found logarithm with base {base} and contents {contents}")
    
    # 01234....910........19
    # log_{base}(contents)
    # 4 + len(base)(4) + 2 + len(contents)(8) + 1 + 1
    # = 8 + len(base)(4) + len(contents)(8)

    eq = (eq[:loc]
          + str(cmath.log(Evaluate(contents, head="  "), Evaluate(base, head="  "))) 
          + eq[loc + 8 + len(base) + len(contents):])
    #eq = eq.replace(f"log_{{{base}}}({contents})", str(cmath.log(Evaluate(contents), Evaluate(base))))

  # P - Parenthesis
  while "(" in eq or "[" in eq:
    pair = ("(", ")") if "(" in eq else ("[", "]")
    contents = Between(eq, 0, pair[0], pair[1])
    #print(head + f"  Found {'parenthesis' if pair[0] == '(' else 'absolute value'} with contents {contents}")
    
    eq = eq.replace(f"{pair[0]}{contents}{pair[1]}", 
                    str(abs(Evaluate(contents, head="  ")) if pair[0] == "[" else Evaluate(contents, head="  "))
                       .replace(pair[0], "").replace(pair[1], "")
                   )

  # E - Exponents
  loc = None
  while (loc := eq.find("^")) != -1:
    exp = Between(eq, loc, "{", "}")
    
    i = 0
    base = eq[:loc]
    while not isFloat(base):
      i += 1
      base = eq[:loc][i:]
    
    #print(head + f"  Found exponent with base {base} and exponent {exp}")
    eq = eq[:loc - len(base)] + str(pow(toFloat(base), Evaluate(exp, head="  "))) + eq[3 + loc + len(exp):]
    #eq = eq.replace(base + "^{"+exp+"}",
    #                str(pow(toFloat(base), Evaluate(exp))))

  # E - Exponents (square root)
  loc = None
  while (loc := eq.find("\\sqrt")) != -1:
    nthroot = Between(eq, loc + 5, "{", "}")
    contents = Between(eq, loc + 5 + len(nthroot) + 2, "{", "}")
    #print(head + f"  Found a {nthroot} degree radical containing {contents}")
    
    eq = eq[:loc] + str(pow(Evaluate(contents, head="  "), 1 / Evaluate(nthroot, head="  "))) + eq[loc + len(nthroot) + len(contents) + 9:]
    #eq = eq.replace(r"\sqrt{"+nthroot+"}" + "{"+contents+"}", 
    #                str(pow(Evaluate(contents), 1 / Evaluate(nthroot))))

  # D - Division (Fractions have priority)
  loc = None
  while (loc := eq.find("\\frac")) != -1:
    numer = Between(eq, loc + 5, "{", "}")
    denom = Between(eq, loc + len(numer) + 7, "{", "}")
    #print(head + f"  Found a fraction with numerator {numer} and denominator {denom}")
    
    eq = eq[:loc] + str(Evaluate(numer, head="  ") / Evaluate(denom, head="  ")) + eq[loc + len(numer) + len(denom) + 9:]
    #eq = eq.replace(f"\\frac{{{numer}}}{{{denom}}}",
    #                str(Evaluate(numer) / Evaluate(denom)))

  # Permutations and Combinations
  loc = None
  while (loc := eq.find("\\comb")) != -1 or (loc := eq.find("\\perm")) != -1:
    op = r"*\comb*" if eq[loc + 1] == "c" else r"*\perm*"
    
    i = 0
    while not isFloat(eq[:loc - 1][i:]):
      i += 1
    n = eq[:loc][i:]
    
    i = len(eq)
    while not isFloat(eq[loc + 6:][:i]):
      i -= 1
    r = eq[loc + 5:][:i]
    
    eq = eq.replace(n + op + r, str(math.perm(int(n), int(r)) / (math.factorial(int(r)) if op[2] == "c" else 1)))

  # Reevaluate parenthesis because complex numbers
  while "(" in eq:
    contents = Between(eq, 0, "(", ")")
    #print(head + f"  Found parenthesis with contents {contents}")
    
    eq = eq.replace(f"({contents})", str(Evaluate(contents, head="  ")).replace("(", "").replace(")", ""))

  # DMAS - In that order
  curOp = 0
  progress = 0
  doNotCheck = False
  #print(head + f"  Finding operations in {eq}")
  
  #start = monotonic_ns()
  while doNotCheck or not isFloat(eq):
    if (progress := eq.find(("/", "*", "+", "-")[curOp], progress)) == -1:
      curOp += 1 if curOp < 3 else -1
      progress = 0
      doNotCheck = True
      continue
    
    doNotCheck = False

    lenEq = len(eq)

    i = 0
    befOp = eq[:progress]
    first = befOp
    while not isFloat(first) or first[0] == " ": 
      first = befOp[(i := i + 1):]
    
    aftOp = eq[progress + 1:]
    j = lenEq - progress - 1
    second = aftOp
    while not isFloat(second):
      second = aftOp[:(j := j - 1)]

    #print(head + f"    found operator {curOp} with first {first} and second {second}")
    #print(f"result: {str(operate[curOp](first, second))}")

    repl = str(operate[curOp](first, second))
    if repl[0] == "(":
      repl = repl[1:-1]

    eq = eq[:i] + repl + eq[lenEq - (lenEq - progress - 1) + j:]
    progress -= (i - len(repl) + 1)

    #print(f"eq: {eq}")
  
  #print(head + f"  operated eq in {(monotonic_ns() - start) / 1_000_000}ms")

  ans = toFloat(eq)
  #print(head + f"Finished evaluating; result: {ans}\n")
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
      eq = eq[:i + 1] + " * " + eq[i + 1:] # Insert multiplication
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


