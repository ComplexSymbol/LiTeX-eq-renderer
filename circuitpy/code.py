import LiTeX as LT # type: ignore
import Evaluator as EV # type: ignore
import SPI
import time

print("Initializing Display...")
SPI.initialize_display()
time.sleep(1)
SPI.software_reset()

print("Clearing Display...")
SPI.clear_display()
SPI.send_command(SPI.INVR_OFF)

print("Wait 2 sec...")
time.sleep(2)

eqs = [r"1",
       r"1 + ",
       r"1 + \e",
       r"1 + \e^{`}",
       r"1 + \e^{2}",
       r"1 + \e^{2\pi}",
       r"1 + \e^{2\pi\im}",
       r"1 + \e^{2\pi\im} - ",
       r"1 + \e^{2\pi\im} - 3",
       r"1 + \e^{2\pi\im} - 3\sqrt{2}{`}",
       r"1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{`}{`}}",
       r"1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(`)}{`}}",
       r"1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(4)}{`}}",
       r"1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(4)}{3}}",
      ]

renderEQ = None
for eqNum in range(0, len(eqs)):
  renderEQ = LT.genRender(eqs[eqNum])
  print("Sending Data...")
  SPI.send_bitmap(renderEQ, 0)

equation = eqs[-1]
eq = equation

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
del eq, ans, equation

#LT.print2dArray(renderEQ)
#LT.print2dArray(renderANS)

print("Sending Data...")
SPI.send_bitmap(renderEQ, 0)
SPI.send_bitmap(renderANS, 64 - len(renderANS))

print("Press enter to close...")
_ = input()

print("Clearing, Software reset, and closing SPI...")
SPI.clear_display()
SPI.software_reset()
SPI.spi.unlock()