import LiTeX as LT # type: ignore
import Evaluator as EV # type: ignore
import SPI
import time

if False:
  start = time.time()
  rounds = 10_000
  for i in range(rounds):
    LT.merge2dArrays([[True, False, True, False, True],
                      [True, False, True, False, True],
                      [True, False, True, False, True],
                      [True, False, True, False, True],
                      [True, False, True, False, True],
                      [True, False, True, False, True],
                      [True, False, True, False, True],
                      [True, False, True, False, True],
                      [True, False, True, False, True],
                      [True, False, True, False, True]],
                    [[False, True, False, True, False],
                      [False, True, False, True, False],
                      [False, True, False, True, False],
                      [False, True, False, True, False],
                      [False, True, False, True, False],
                      [False, True, False, True, False],
                      [False, True, False, True, False],
                      [False, True, False, True, False],
                      [False, True, False, True, False],
                      [False, True, False, True, False]], 0, 0)
  end = time.time()
  print(f"NEW: {rounds} additions completed in {end - start}s")

  start = time.time()
  rounds = 10_000
  for i in range(rounds):
    LT.oldMerge2dArrays([[True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True]],
                       [[False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False]], 0, 0)
  end = time.time()
  print(f"OLD: {rounds} additions completed in {end - start}s")

  start = time.time()
  rounds = 10_000
  for i in range(rounds):
    LT.GPTMerge2dArrays([[True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True],
                         [True, False, True, False, True]],
                       [[False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False],
                         [False, True, False, True, False]], 0, 0)
  end = time.time()
  print(f"GPT: {rounds} additions completed in {end - start}s")

if True:
  print("Initializing Display...")
  SPI.initialize_display()
  time.sleep(1)
  SPI.software_reset()

  print("Clearing Display...")
  SPI.clear_display()
  SPI.send_command(SPI.INVR_OFF)

  print("Wait 2 sec...")
  time.sleep(2)

  eqs = [r"\frac{`}{`}",
        r"\frac{`}{0}",
        r"\frac{`}{0.}",
        r"\frac{`}{0.8}",
        r"\frac{log_{`}(`)}{0.8}",
        r"\frac{log_{3}(`)}{0.8}",
        r"\frac{log_{3}(1)}{0.8}",
        r"\frac{log_{3}(1 + )}{0.8}",
        r"\frac{log_{3}(1 + \e)}{0.8}",
        r"\frac{log_{3}(1 + \e^{`})}{0.8}",
        r"\frac{log_{3}(1 + \e^{2})}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi})}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi\im})}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi\im} - )}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi\im} - 3)}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi\im} - 3\sqrt{2}{`})}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{`}{`}})}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(`)}{`}})}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(4)}{`}})}{0.8}",
        r"\frac{log_{3}(1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(4)}{3}})}{0.8}",
        ]

  renderEQ = [[]]
  renderANS = [[]]
  for eqNum in range(len(eqs)):
    equation = eqs[eqNum]
    eq = equation
    renderEQ = LT.genRender(equation)

    try:
      if "=" in eq:
        indx = eq.index("=")
        eq = eq[:indx] + " - ("+eq[indx + 1:]+")"
      
      ans = EV.Evaluate(eq, solve="x" in eq, replace=True, guess=2, shouldGuessImag=False)
      ans = (float(ans) if isinstance(ans, float) else
            "{0:10f}".format(ans.real).rstrip("0").rstrip(".") + ("{0:+10f}".format(ans.imag).rstrip("0").rstrip(".") + r"\im" if
                  ans.imag != 0 else "")).replace("j", r"\im")
      ans = "~" + ans[1:] if ans[0] == "-" else ans
      ans = ans.replace("j", "\im")
      renderANS = LT.genRender(("x" if "x" in equation else "") + "=" + ans)
    except:
      renderANS = [[]]

    print("Sending Data...")
    SPI.send_bitmap(renderEQ, 0)
    SPI.send_bitmap([[False] * 128] * 10, 54)
    if renderANS != [[]]: SPI.send_bitmap(renderANS, 64 - len(renderANS))
    
    time.sleep(0.3)

  print("Press enter to close...")
  _ = input()

  print("Clearing, Software reset, and closing SPI...")
  SPI.clear_display()
  SPI.software_reset()
  SPI.spi.unlock()