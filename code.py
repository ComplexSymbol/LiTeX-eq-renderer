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

print("Wait 1 sec...")
time.sleep(1)

eqs = [
  r"1",
  r"1 + ",
  r"1 + \e",
  r"1 + \e^{`}",
  r"1 + \e^{2}",
  r"1 + \e^{2\pi}",
  r"1 + \e^{2\pi\im}",
  r"1 + \e^{2\pi\im} -",
  r"1 + \e^{2\pi\im} - 3",
  r"1 + \e^{2\pi\im} - 3\sqrt{2}{`}",
  r"1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{`}{`}}",
  r"1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(`)}{`}}",
  r"1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(4)}{`}}",
  r"1 + \e^{2\pi\im} - 3\sqrt{2}{\frac{sin(4)}{3}}",
]

eqs = [
  r"1+\e^{2\pi\im}"
]

renderEQ = None
print()
for eqNum in range(len(eqs)):
  start = time.monotonic_ns()
  renderEQ = LT.genRender(eqs[eqNum])
  print(f"Rendered in {(time.monotonic_ns() - start) / 1_000_000}ms")

  print("Sending Data...\n")
  SPI.send_render(renderEQ, 0)

  #LT.testPrint(renderEQ, True)

equation = eqs[eqNum]
eq = equation

if "=" in eq:
  indx = eq.index("=")
  eq = eq[:indx] + " - ("+eq[indx + 1:]+")"

start = time.monotonic_ns()
ans = EV.Evaluate(eq, solve="x" in eq, repl=True, guess=2, shouldGuessImag=False)
print(f"Evaluated in {(time.monotonic_ns() - start) / 1_000_000}ms")

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
SPI.send_render(renderEQ, 0)
SPI.send_render(renderANS, 64 - len(renderANS.bitmap))

print("Press enter to close...")
_ = input()

print("Clearing, Software reset, and closing SPI...")
SPI.clear_display()
SPI.software_reset()
SPI.spi.unlock()