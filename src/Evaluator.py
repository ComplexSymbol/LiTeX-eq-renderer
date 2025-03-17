import math

trigs = {'sin': lambda x: math.sin(x),
         'cos': lambda x: math.cos(x),
         'tan': lambda x: math.tan(x),
         'csc': lambda x: 1 / math.sin(x),
         'sec': lambda x: 1 / math.sec(x),
         'cot': lambda x: 1 / math.cot(x)}

operate = {'+': lambda x, y: toFloat(x) + toFloat(y),
           '-': lambda x, y: toFloat(x) - toFloat(y),
           '*': lambda x, y: toFloat(x) * toFloat(y),
           '/': lambda x, y: toFloat(x) / toFloat(y)}

# Follows strict PEDMAS
def Evaluate(eq, replace = False):
  global trigs, operate
  
  if isFloat(eq):
    return toFloat(eq)
  
  print(f"Standardizing eq : '{eq}'")
  
  if replace:
    #replace - with +- because 3-2^{4} evaluates as 316
    eq = eq.replace("-", "+-")
    eq = eq.replace("~", "-")
    eq = eq.replace("log-", "log_")
  
  # Add implicit multiplication
  for i in range(len(eq) - 1):
    # 3 main causes: num*func, paren*func, paren*paren
    if ((eq[i].isdigit() and eq[i + 1] == "\\") or # 5\pi
        (eq[i].isdigit() and eq[i + 1] == "(") or # 2(3 ...
        (eq[i].isdigit() and eq[i + 1].isalpha() and eq[i + 1] != "j") or # 9sin(...
        (eq[i].isalpha() and eq[i + 1] == "\\") or # \pi\e, X: (\pi
        (eq[i] == ")" and eq[i + 1] == "\\") or # ...4)\pi
        (eq[i] == ")" and eq[i + 1] == "(") or # ...3)(6...
        (eq[i] == "}" and eq[i + 1].isdigit())): # ...2}7
      eq = eq[:i + 1] + "*" + eq[i + 1:] # Insert multiplication
  
  print(f"Evaluating \'{eq}\'")
  
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
  print(f"   Eq is {eq} after replacing constants")
  
  # P - Parenthetical function (trig)
  while any(trigs in eq for trigs in ["sin", "cos", "tan", "sec", "csc", "cot"]):
    func = "sin" if "sin" in eq else (
           "cos" if "cos" in eq else (
           "tan" if "tan" in eq else (
           "csc" if "csc" in eq else (
           "sec" if "sec" in eq else (
           "cot" if "cot" in eq else (
           None))))))

    contents = Between(eq[eq.index(func) + 3:], "(", ")")

    print(f"  Found trig function {func} with contents {contents}")
    eq = eq.replace(f"{func}({contents})", 
                    str(SpecialTrig(func, Evaluate(contents), False)).replace("(", "").replace(")", ""))
  print(f"   Eq is {eq} after evaluating trig functions")
  
  # P - Parenthetical function (log)  
  while "log" in eq: 
    print("  Found logarithm!")
    location = eq.index("log")
    base = Between(eq[location + 3:], "{", "}")
    contents = Between(eq[location + len(base) + 2:], "(", ")")
    
    eq = eq.replace("log_{"+base+"}" + f"({contents})", 
                    str(math.log(Evaluate(contents), Evaluate(base))).replace("(", "").replace(")", ""))
  
  print(f"   Eq is {eq} after evaluating logarithms")
  
  # P - Parenthesis
  while "(" in eq:
    contents = Between(eq, "(", ")")
    if isFloat(contents):
      break
    
    eq = eq.replace(f"({contents})", 
                    str(Evaluate(contents)))
  print(f"   Eq is {eq} after evaluating parentheticals")

  # E - Exponents
  while "^" in eq:
    exp = Between(eq[eq.index("^"):], "{", "}")
    base = None
    
    i = 0
    while not isFloat(eq[:eq.index("^")][i:]): i += 1
    base = eq[:eq.index("^")][i:]
    
    print(f"  Found exponent with base {base} and exponent {exp}")
    eq = eq.replace(base + "^{"+exp+"}",
                    str(toFloat(pow(toFloat(base), Evaluate(exp)))).replace("(", "").replace(")", ""))
  print(f"   Eq is {eq} after evaluating exponents")

  # E - Exponents (square root)
  while r"\sqrt" in eq:
    start = eq.find(r"\sqrt") + 5
    nthroot = Between(eq[start:], "{", "}")
    contents = Between(eq[start + len(nthroot) + 2:], "{", "}")
    
    print(f"  Found an {nthroot} degree radical containing {contents}")
    
    eq = eq.replace(r"\sqrt{"+nthroot+"}" + "{"+contents+"}", 
                    str(toFloat(pow(Evaluate(contents), 1 / Evaluate(nthroot)))).replace("(", "").replace(")", ""))
  print(f"   Eq is {eq} after evaluating radicals")
  
  # D - Division (Fractions have priority)
  while r"\frac" in eq:
    start = eq.find(r"\frac") + 5
    numer = Between(eq[start:], "{", "}")
    denom = Between(eq[start + len(numer) + 2:], "{", "}")
    
    eq = eq.replace(r"\frac{"+numer+"}" + "{"+denom+"}", 
                    str(toFloat(Evaluate(numer) / Evaluate(denom))))
  print(f"   Eq is {eq} after evaluating fractions")

  # DMAS - In that order
  skip = 0
  while set(eq[skip:]) & frozenset("/*+-") and not isFloat(eq[skip:]):
    curOp = "/" if "/" in eq[skip:] else (
            "*" if "*" in eq[skip:] else (
            "+" if "+" in eq[skip:] else (
            "-" if "-" in eq[skip:] else (
            None))))
    
    before = eq[skip:][:eq[skip:].index(curOp)]
    i = 0
    while not isFloat(before[i:]): i += 1
    first = before[i:]
    
    after = eq[skip:][eq[skip:].index(curOp) + 1:]
    i = len(after)
    while not isFloat(after[:i]):
      i -= 1
    second = after[:i]
    
    if isFloat(f"{first}{curOp}{second}"):
      skip = eq[skip:].index(curOp) + 1
      print(f"setting skip to {skip}")
      continue
    
    print(f"  Found operator \'{curOp}\' with first \'{first}\' and second \'{second}\'")
    print(f"  Result: {operate[curOp](first, second)}")
    eq = eq.replace(f"{first}{curOp}{second}", 
                    str(toFloat(operate[curOp](first, second))))
    skip = 0
    
  print(f"   Eq is {eq} after evaluating operations")
  
  
  sign = 1
  if eq[0] == "-":
    sign = -1
    eq = eq[1:]
  
  ans = toFloat(eq)
  print(f"Finished evaluating; result: sign {sign}, ans {ans}, multans {sign * ans}")
  return sign * ans;

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

def SpecialTrig(func, x, simplify):
  global trigs
  
  x = toFloat(x)
  if isinstance(x, complex):
    print("JOE " + '('+str(math.e) + "^{j*"+ str(x) +"}+-" + str(math.e) + "^{-j*"+ str(x) +"})/(2j)")
    return Evaluate('('+str(math.e) + "^{j*"+ str(x) +"}+-" + str(math.e) + "^{-j*"+ str(x) +"})/(2j)")
  
  if not simplify:
    return trigs[func](x)
  
  if (x == math.pi / 6):
    if func == "sin":
      return r"\frac{1}{2}"
    elif func == "cos":
      return r"\frac{\sqrt{2}{3}}{2}"
    elif func == "tan":
      return r"\frac{\sqrt{2}{3}}{3}"
    elif func == "sec":
      return r"\frac{2\sqrt{2}{3}}{3}"
    elif func == "cot":
      return r"\sqrt{2}{3}"
  elif x == math.pi / 4:
    if func == "sin":
      return r"\frac{\sqrt{2}{2}}{2}"
    elif func == "cos":
      return r"\frac{\sqrt{2}{2}}{2}"
    elif func == "csc":
      return r"\sqrt{2}{2}"
    elif func == "sec":
      return r"\sqrt{2}{2}"
  elif x == math.pi / 3:
    if func == "sin":
      return SpecialTrig("cos", math.pi / 6, simplify)
    elif func == "cos":
      return SpecialTrig("sin", math.pi / 6, simplify)
    elif func == "tan":
      return SpecialTrig("cot", math.pi / 6, simplify)
    elif func == "csc":
      return SpecialTrig("sec", math.pi / 6, simplify)
    elif func == "sec":
      return SpecialTrig("csc", math.pi / 6, simplify)
    elif func == "cot":
      return SpecialTrig("tan", math.pi / 6, simplify)
  elif x > math.pi / 2 and x < math.pi:
    if func == "sin" or func == "csc":
      return SpecialTrig(func, math.pi - x, simplify)
    else: return "-" + SpecialTrig(func, math.pi - x, simplify)
  elif x > math.pi and x < 3 * math.pi / 2:
    if func == "cos" or func == "sec":
      return SpecialTrig(func, math.pi - x, simplify)
    else: return "-" + SpecialTrig(func, math.pi - x, simplify)
  elif x > math.pi and x < 3 * math.pi / 2:
    if func == "tan" or func == "cot":
      return SpecialTrig(func, math.pi - x, simplify)
    else: return "-" + SpecialTrig(func, math.pi - x, simplify)
  
  return str(trigs[func](x))

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
  string = str(string)
  
  # Complex or imaginary
  if "j" in string:
    return complex(round(complex(string).real, 6), round(complex(string).imag, 6))
  
  else: return round(float(string), 6)
  
  