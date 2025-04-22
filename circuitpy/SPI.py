import board
import digitalio
import busio
import array
import time

# Command constants:
BIAS_SEL = 0b10100010
SEG_DIR = 0b10100000
COM_DIR = 0b11000000

REG_RATIO = 0b00100000
ELEC_VOL1 = 0b10000001
ELEC_VOL2 = 0b00000000

PWR_CTL = 0b00101000
DISP_ON = 0b10101111
DISP_OFF = 0b10101110

SFTWR_RST = 0b11100010

INVR_ON = 0b10100111
INVR_OFF = 0b10100110

# Data command constants:
STRT_LINE = 0b01000000
PAGE_ADDR = 0b10110000
CLMN_ADR1 = 0b00010000
CLMN_ADR2 = 0b00000000

# Pin assignments (SPI)
CS_PIN = board.D10  # Chip Select   FNL: 10
DC_PIN = board.D14  # Data/Command  FNL: 14
RST_PIN = board.D9  # Reset         FNL: 9
SCK_PIN = board.D13  # Clock        FNL: 13
MOSI_PIN = board.D11  # MOSI        FNL: 11

# Pin initializations (SPI)
cs = digitalio.DigitalInOut(CS_PIN)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True  # Deselect display

dc = digitalio.DigitalInOut(DC_PIN)
dc.direction = digitalio.Direction.OUTPUT
dc.value = True  # Default to data mode

rst = digitalio.DigitalInOut(RST_PIN)
rst.direction = digitalio.Direction.OUTPUT
rst.value = True  # Default reset state

spi = busio.SPI(clock=SCK_PIN, MOSI=MOSI_PIN, MISO=None)
if not spi.try_lock(): raise OSError("Failed to lock SPI bus.")

spi.configure(baudrate=10_000_000)

# Helper functions
def send_command(cmd):
    dc.value = False  # Command mode
    cs.value = False  # Select the display

    spi.write(array.array("B", [cmd]))

    cs.value = True  # Deselect the display


def send_data(data):
    dc.value = True  # Data mode
    cs.value = False  # Select the display

    spi.write(array.array("B", [data]))

    cs.value = True  # Deselect the display


def hardware_reset():
    rst.value = False
    time.sleep(0.1)

    rst.value = True
    time.sleep(0.1)


def initialize_display():
    hardware_reset()

    send_command(BIAS_SEL | 0b00000000)  # Bias select (1/7)
    send_command(SEG_DIR | 0b00000001)  # Normal SEG direction
    send_command(COM_DIR | 0b00000000)  # Normal COM direction

    send_command(REG_RATIO | 0b00000111)  # 111 (7) Reg Ratio
    send_command(ELEC_VOL1)
    send_command(ELEC_VOL2 | 0b00011111)  # Middle (0x1F) electronic volume

    send_command(PWR_CTL | 0b00000111)  # Power control
    send_command(DISP_ON)


def software_reset():
    send_command(SFTWR_RST)
    adjust_contrast(0x28)
    send_command(STRT_LINE | 0x00)

def adjust_contrast(val):
    if val < 0:
        val = 0

    elif val > 63:
        val = 63

    send_command(ELEC_VOL1)
    send_command(ELEC_VOL2 | val)

def clear_display():
    send_command(STRT_LINE | 0x00)
    send_command(PAGE_ADDR | 0x00)

    for y in range(8):
        send_command(PAGE_ADDR | y)

        send_command(CLMN_ADR1 | 0x00)
        send_command(CLMN_ADR2 | 0x00)

        for x in range(132):
            send_data(0x00)


def send_render(render, k = 0):
    send_command(PAGE_ADDR | 0x00)
    send_command(CLMN_ADR1 | 0x00)
    send_command(CLMN_ADR2 | 0x00)

    render.bitmap = [0] * (k - (8 * (k // 8))) + render.bitmap
    k = (8 * (k // 8))

    for y in range(0, len(render.bitmap), 8):
        send_command(PAGE_ADDR | ((y + k) // 8))
        send_command(CLMN_ADR1 | 0x00)
        send_command(CLMN_ADR2 | 0x00)

        for x in range(render.width):
            lenRender = len(render.bitmap)
            send_data((0b10000000 if (y + 7 < lenRender and (render.bitmap[y + 7] >> (render.width - x - 1)) & 1) else 0) |
                      (0b01000000 if (y + 6 < lenRender and (render.bitmap[y + 6] >> (render.width - x - 1)) & 1) else 0) |
                      (0b00100000 if (y + 5 < lenRender and (render.bitmap[y + 5] >> (render.width - x - 1)) & 1) else 0) |
                      (0b00010000 if (y + 4 < lenRender and (render.bitmap[y + 4] >> (render.width - x - 1)) & 1) else 0) |
                      (0b00001000 if (y + 3 < lenRender and (render.bitmap[y + 3] >> (render.width - x - 1)) & 1) else 0) |
                      (0b00000100 if (y + 2 < lenRender and (render.bitmap[y + 2] >> (render.width - x - 1)) & 1) else 0) |
                      (0b00000010 if (y + 1 < lenRender and (render.bitmap[y + 1] >> (render.width - x - 1)) & 1) else 0) |
                      (0b00000001 if (y + 0 < lenRender and (render.bitmap[y + 0] >> (render.width - x - 1)) & 1) else 0))
