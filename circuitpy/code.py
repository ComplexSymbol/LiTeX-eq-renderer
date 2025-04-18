import LiTeX as LT # type: ignore
import Evaluator as EV # type: ignore

equation = r"x^{\frac{1}{x}}=0.5"
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

renderEQ = LT.genRender(equation)
renderANS = LT.genRender(("x" if "x" in equation else "") + "=" + ans)

LT.print2dArray(renderEQ)
LT.print2dArray(renderANS)
