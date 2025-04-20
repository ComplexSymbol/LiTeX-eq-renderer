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
  0: lambda x, y: toFloat(x) / toFloat(y),
  1: lambda x, y: toFloat(x) * toFloat(y),
  2: lambda x, y: toFloat(x) + toFloat(y),
  3: lambda x, y: toFloat(x) - toFloat(y)
}

# Follows strict PEDMAS
def Evaluate(eq, solve = False, replace = False, guess = 10, shouldGuessImag = False, printAhead = ""):
  global trigs, operate

  if isFloat(eq):
    #print(f"Single number EQ {eq}")
    return toFloat(eq)

  #print(printAhead + f"Standardizing eq: '{eq}'")

  # Standardize equation
  if replace:
    if '`' in eq:
      raise ValueError("Incomplete expression")

    #eq = eq.replace(" - ", " +-")
    eq = eq.replace("~", "-")
    eq = eq.replace("log-", "log_")
    eq = eq.replace(r"\im", "j")

  # Add implicit multiplication
  eq = impMult(eq)

  # Change constants into numbers
  specials = ["pi", "e"]
  values = { 'e': math.e,
             'pi': math.pi,
           }
  tries = [("\\" + sp) in eq for sp in specials]
  while any(tries):
    eq = eq.replace("\\" + specials[tries.index(True)],
                    str(values[specials[tries.index(True)]]))
    tries[tries.index(True)] = False
  try: del tries, specials, values
  except: pass

  # Redo implicit multiplication because the constants have turned into numbers
  eq = impMult(eq)

  # Undo implicit multiplication for permutations and combinations (4\perm3 != 4*\perm*3)
  eq = eq.replace(r"*\perm*", r"\perm").replace(r"*\comb*", r"\comb")

  # Solve the equation if it should be solved
  if solve:
    return NewtonMethod(eq, guess, 8, shouldGuessImag)

  #print(printAhead + f"Evaluating \'{eq}\'")

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

    #print(printAhead + f"  Found trig function {func} with contents {contents}")
    eq = eq.replace(f"{func[1:] + "^{-1}" if func[0] == "a" else func}({contents})",
                    str(trigs[func](Evaluate(contents, printAhead=printAhead + "  "))))
  try: del contents, func 
  except: pass

  # P - Parenthetical function (log)
  while "log" in eq:
    location = eq.index("log")
    base = Between(eq[location + 3:], "{", "}")
    contents = Between(eq[location + len(base) + 6:], "(", ")")
    #print(printAhead + f"  Found logarithm with base {base} and contents {contents}")

    eq = eq.replace("log_{"+base+"}" + f"({contents})",
                    str(cmath.log(Evaluate(contents, printAhead=printAhead + "  "), Evaluate(base, printAhead=printAhead + "  "))))
  try: del location, base, contents
  except: pass

  # P - Parenthesis
  while "(" in eq:
    contents = Between(eq, "(", ")")
    #print(printAhead + f"  Found parenthesis with contents{contents}")

    sign = 1
    if eq[eq.index("(" + contents) - 1] == "-":
      sign = -1
      eq = eq[:eq.index("(" + contents) - 1] + eq[eq.index("(" + contents):]

    eq = eq.replace(f"({contents})",
                    str(sign * Evaluate(contents, printAhead=printAhead + "  ")).replace("(", "").replace(")", ""), 1)
  try: del contents, sign
  except: pass

  # E - Exponents
  while "^" in eq:
    exp = Between(eq[eq.index("^"):], "{", "}")
    base = None

    i = 0
    base = eq[:eq.index("^")]
    while not isFloat(base):
      i += 1
      base = eq[:eq.index("^")][i:]

    if eq[eq.index(base) - 1] == "+":
      base = base[1:]

    #print(printAhead + f"  Found exponent with base {base} and exponent {exp}, result: {str(toFloat(pow(toFloat(base), Evaluate(exp))))}")
    eq = eq.replace(base + "^{"+exp+"}",
                    str(toFloat(pow(toFloat(base), Evaluate(exp, printAhead=printAhead + "  ")))))
  try: del exp, base, i
  except: pass

  # E - Exponents (square root)
  while r"sqrt" in eq:
    start = eq.index(r"\sqrt") + 5
    nthroot = Between(eq[start:], "{", "}")
    contents = Between(eq[start + len(nthroot) + 2:], "{", "}")
    #print(printAhead + f"  Found a {nthroot} degree radical containing {contents}")

    eq = eq.replace(r"\sqrt{"+nthroot+"}" + "{"+contents+"}",
                    str(toFloat(pow(Evaluate(contents, printAhead=printAhead + "  "), 1 / Evaluate(nthroot, printAhead=printAhead + "  ")))))
  try: del start, nthroot, contents
  except: pass

  # D - Division (Fractions have priority)
  while r"frac" in eq:
    start = eq.index(r"\frac") + 5
    numer = Between(eq[start:], "{", "}")
    denom = Between(eq[start + len(numer) + 2:], "{", "}")
    #print(printAhead + f"  Found a fraction with numerator {numer} and denominator {denom}")

    eq = eq.replace(r"\frac{"+numer+"}" + "{"+denom+"}",
                    str(toFloat(Evaluate(numer, printAhead=printAhead + "  ") / Evaluate(denom, printAhead=printAhead + "  "))))
  try: del start, numer, denom
  except: pass

  # Reevaluate parenthesis because complex numbers
  eq = eq.replace("(", "").replace(")", "")

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
  try: del isComb, indx, i, n, r
  except: pass

  # DMAS - In that order
  eq = eq.replace("+-", "-")
  eq = ("0" + eq) if eq[0] == "-" else eq
  progress = -1
  curOp = 0
  #print(printAhead + f"  Finding operations in {eq}")
  while set(eq) & frozenset("/*+-") and not isFloat(eq):
    opStr = ("/", "*", "+", "-")[curOp]

    if not opStr in eq[max(0, progress):]:
      curOp += 1 if curOp < 3 else -1
      progress = -1
      continue

    #print(printAhead + f"({opStr}) |--| {eq[progress:]}")

    progress += 1
    if eq[progress] != opStr or eq[progress - 1] == "e":
      continue

    if " " in eq and curOp == 3:
      eq = eq.replace(" ", "")
      progress = -1
      continue

    if progress == 0 and eq[0] == "-":
      progress += 1
      continue

    i = 0
    while not isFloat(eq[:progress][i:]): i += 1
    first = eq[:progress][i:]

    i = len(eq[progress + 1:])
    while not isFloat(eq[progress + 1:][:i]): i -= 1
    second = eq[progress + 1:][:i]

    repl = str(toFloat(operate[curOp](first, second))).replace("(", "").replace(")", "")
    #print(printAhead + f"  Found operator \'{eq[progress]}\' with first \'{first}\' and second \'{second}\'. Result: {repl}")
    eq = eq.replace(f"{first}{eq[progress]}{second}", repl)

    #print(printAhead + f"setting progress from {progress} to {progress - len(first) + len(repl) - 1}")
    progress = progress - len(first) + len(repl) - 1
    eq = eq.replace("+-", "-")
    #print(printAhead + eq)
  try: del progress, curOp, opStr, progress, i, repl
  except: pass

  ans = toFloat(eq)
  #print(printAhead + f"  Finished evaluating; result: {ans}")
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
        (eq[i].isdigit() and eq[i + 1].isalpha() and eq[i + 1] != "e" and eq[i + 1] != "j") or # 9sin(... but not 3e
        (eq[i].isalpha() and eq[i + 1].isdigit()) or # \pi3...
        (eq[i].isalpha() and eq[i + 1] == "\\") or # \pi\e, X: (\pi
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
def Between(string, char1, char2):
  for i in range(len(string)):
    if string[i] == char2 and (string[:i].count(char1) == string[:i + 1].count(char2)):
      return string[string.index(char1) + 1 : i]

  raise ValueError(f"Unable to find contents between {char1} and {char2}")

def isFloat(string):
  if string[0] == "+": return False

  try:
    toFloat(string)
    return True

  except ValueError:
    return False

def toFloat(string):
  string = complex(string)

  if string.imag == 0:
    return string.real
  else:
    return string


inc = 0.001
def NewtonMethod(eq, guess, accuracy, shouldGuessImag, alter = 1, epsilon = 0.00001, maxIter = 40):
  if shouldGuessImag:
    guess = guess + 1j

  for i in range(maxIter):
    if i == maxIter - 1:
      raise ValueError(f"No root found under {maxIter} iterations")

    inputEQ = eq.replace("x", str(guess))
    funcAtGuess = complex(Evaluate(inputEQ))
    if abs(funcAtGuess.real + funcAtGuess.imag) < 2 * math.pow(10, -accuracy - 1):
      break

    derivAtGuess = (funcAtGuess - Evaluate(eq.replace("x", str(guess - inc)))) / inc
    if abs(derivAtGuess) < epsilon:
      raise ValueError(f"Function too flat... Possible asymptote. Try another guess. {derivAtGuess}")

    testGuess = (guess * derivAtGuess - funcAtGuess) / derivAtGuess
    if not shouldGuessImag and complex(Evaluate(eq.replace("x", str(testGuess)))).imag != 0:
      doubleDerivAtGuess = complex((derivAtGuess - ((funcAtGuess - Evaluate(eq.replace("x", str(guess - inc - inc)))) / inc)) / inc)
      print(f"{'Decrimenting' if doubleDerivAtGuess.real < 0 else 'Incrementing'} guess {guess} by {alter}")
      guess += -alter if doubleDerivAtGuess.real < 0 else alter
      continue

    guess = testGuess
    print(f"New Guess: {guess}")


  return complex(round(complex(guess).real, accuracy), round(complex(guess).imag, accuracy))
