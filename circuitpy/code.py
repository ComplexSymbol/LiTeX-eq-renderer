import LiTeX as LT # type: ignore
import Evaluator as EV # type: ignore
import time

if True:
  #print("Initializing Display...")
  #SPI.initialize_display()
  #time.sleep(1)
  #SPI.software_reset()

  #print("Clearing Display...")
  #SPI.clear_display()
  #SPI.send_command(SPI.INVR_OFF)

  #print("Wait 2 sec...")
  #time.sleep(2)
  eqs = [
         r"log_{(\frac{\frac{1}{log_{2}(3)}}{\e\imsin(\pisin(3))})}(2)"
        ]
  
  renderEQ = None
  renderANS = None
  for eqNum in range(len(eqs)):
    equation = eqs[eqNum]
    eq = equation
    renderEQ = LT.genRender(equation, first=True)

    if "=" in eq:
      indx = eq.index("=")
      eq = eq[:indx] + " - ("+eq[indx + 1:]+")"
    
    ans = EV.Evaluate(eq, solve="x" in eq, replace=True, guess=2, shouldGuessImag=False)
    ans = (float(ans) if isinstance(ans, float) else
          "{0:10f}".format(ans.real).rstrip("0").rstrip(".") + ("{0:+10f}".format(ans.imag).rstrip("0").rstrip(".") + r"\im" if
                ans.imag != 0 else "")).replace("j", r"\im")
    ans = "~" + ans[1:] if ans[0] == "-" else ans
    ans = ans.replace("j", r"\im")
    renderANS = LT.genRender(("x" if "x" in equation else "") + "=" + ans, first=True)

    #print("Sending Data...")
    #SPI.send_bitmap(renderEQ, 0)
    #SPI.send_bitmap([[False] * 128] * 10, 54)
    #if renderANS != [[]]: SPI.send_bitmap(renderANS, 64 - len(renderANS))
    
    #time.sleep(0.3)

  LT.testPrint(renderEQ, True)
  LT.testPrint(renderANS, True)

  #print("Press enter to close...")
  #_ = input()

  #print("Clearing, Software reset, and closing SPI...")
  #SPI.clear_display()
  #SPI.software_reset()
  #SPI.spi.unlock()