import time
import SPI
import LiTeX as lt

#Initialize the display
SPI.initialize_display()
time.sleep(1)
SPI.software_reset()

equation = "1+(2^{\\frac{3}{4^5}+6^{7*\\frac{8}{9}}}+10)^11-12^13"
equation = "1+\\frac{1}{2}+\\frac{3^2}{4}"

render = lt.genRender(equation)
lt.print2dArray(render)
SPI.send_bitmap(render)

time.sleep(20)

print("Clearing & Software reset...")
SPI.clear_display()
SPI.software_reset()
print("Done!")
