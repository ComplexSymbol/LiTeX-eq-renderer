import time
import SPI
import LiTeX as litex

# Initialize the display
SPI.initialize_display()
time.sleep(1)
SPI.software_reset()

print("Sending data...")
arr = litex.add2dArrays(litex.readGlyph("2"), litex.readGlyph("."))
arr = litex.add2dArrays(arr, litex.readGlyph("3"))
arr = litex.add2dArrays(arr, litex.readGlyph("x"))
arr = litex.add2dArrays(arr, litex.readGlyph("^2"), True)
arr = litex.add2dArrays(arr, litex.readGlyph("+"))
arr = litex.add2dArrays(arr, litex.readGlyph("9"))
arr = litex.add2dArrays(arr, litex.readGlyph("x"))
arr = litex.add2dArrays(arr, litex.readGlyph("+"))
arr = litex.add2dArrays(arr, litex.readGlyph("1"))
SPI.send_bitmap(arr)
print("Done!")

while input() != "exit":
    pass

print("Clearing & Software reset...")
SPI.clear_display()
SPI.software_reset()
print("Done!")
