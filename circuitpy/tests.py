import Evaluator as EV
import LiTeX as LT

testEQs = [
  r"1": 1.0,
  r"2^{3}": 8+0j,
  r"2^{3} - 1\im": 8-1j,
  r"sin(1)": 0.841470984807897+0j,
  r"sin(1\im)": 1.175201193643801j,
  r"log_{2\im}(3)": 0.258323506157601-0.585407581502881j,
]