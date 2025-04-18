import board
import digitalio
import adafruit_pioasm
import rp2pio
import array
import time
import microcontroller

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
CS_PIN = board.GP9  # Chip Select  FNL: 9
DC_PIN = board.GP11  # Data/Command FNL: 11
RST_PIN = board.GP10  # Reset        FNL: 10
SCK_PIN = board.GP12  # Clock        FNL: 12
MOSI_PIN = board.GP13  # MOSI         FNL: 13

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


# PIO Assembly for SPI
spi_pio_program = """
.side_set 1  ; 1 bit for sideset (clock)
.program spi_pio
    out pins, 1  side 0  ; Clock low
    nop          side 1  ; Output 1 bit, clock high
"""


# Compile and initialize the PIO program
assembledSPI = adafruit_pioasm.assemble(spi_pio_program)

spi = rp2pio.StateMachine(
    program=assembledSPI,
    frequency=0,  # 2KHz for testing on oscilloscope
    first_out_pin=MOSI_PIN,
    out_pin_count=1,
    first_sideset_pin=SCK_PIN,
    sideset_pin_count=1,
    out_shift_right=False,
    pull_threshold=8,  # 8 bits per SPI byte
    auto_pull=True,
)

# Helper functions
def big_endian(n):
    bitArray = [1 if digit == "1" else 0 for digit in bin(n)[2:]]
    bitArray.reverse()

    return int("".join(map(str, bitArray)), 2)


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

    send_command(ELEC_VOL1)
    send_command(ELEC_VOL2 | 0x28)

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


def send_bitmap(bitmap, k):
    send_command(PAGE_ADDR | 0x00)
    send_command(CLMN_ADR1 | 0x00)
    send_command(CLMN_ADR2 | 0x00)

    for y in range(0, len(bitmap), 8):
        send_command(PAGE_ADDR | round((y + k) / 8))

        send_command(CLMN_ADR1 | 0x00)
        send_command(CLMN_ADR2 | 0x03)

        for x in range(len(bitmap[0])):
            send_data(
                int(
                    "".join(
                        map(
                            str,
                            reversed(
                                [
                                    1 if bitmap[y + 0][x] else 0,
                                    0 if y + 1 >= len(bitmap) else (1 if bitmap[y + 1][x] else 0),
                                    0 if y + 2 >= len(bitmap) else (1 if bitmap[y + 2][x] else 0),
                                    0 if y + 3 >= len(bitmap) else (1 if bitmap[y + 3][x] else 0),
                                    0 if y + 4 >= len(bitmap) else (1 if bitmap[y + 4][x] else 0),
                                    0 if y + 5 >= len(bitmap) else (1 if bitmap[y + 5][x] else 0),
                                    0 if y + 6 >= len(bitmap) else (1 if bitmap[y + 6][x] else 0),
                                    0 if y + 7 >= len(bitmap) else (1 if bitmap[y + 7][x] else 0),
                                ]
                            ),
                        )
                    ),
                    2,
                )
            )
