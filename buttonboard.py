import board
import digitalio
import time

# Columns (Pin numbers)
CLMN_0 = board.GP1
CLMN_1 = board.GP1
CLMN_2 = board.GP1
CLMN_3 = board.GP1
CLMN_4 = board.GP1
CLMN_5 = board.GP1

# Rows (Pin numbers)
ROW_0 = board.GP2
ROW_1 = board.GP2
ROW_2 = board.GP2
ROW_3 = board.GP2
ROW_4 = board.GP2
ROW_5 = board.GP2
ROW_6 = board.GP2
ROW_7 = board.GP2
ROW_8 = board.GP2
ROW_9 = board.GP2
ROW_10 = board.GP2


# Columns (Pin initialization)
clmn0 = digitalio.DigitalInOut(CLMN_0)
clmn1 = digitalio.DigitalInOut(CLMN_1)
clmn2 = digitalio.DigitalInOut(CLMN_2)
clmn3 = digitalio.DigitalInOut(CLMN_3)
clmn4 = digitalio.DigitalInOut(CLMN_4)
clmn5 = digitalio.DigitalInOut(CLMN_5)

columns = [clmn0, clmn1, clmn2, clmn3, clmn4, clmn5]

for i in range(len(columns)):
    columns[i].direction = digitalio.Direction.INPUT
    columns[i].pull = digitalio.Pull.DOWN

# Rows (Pin initialization
row0 = digitalio.DigitalInOut(ROW_0)
row1 = digitalio.DigitalInOut(ROW_1)
row2 = digitalio.DigitalInOut(ROW_2)
row3 = digitalio.DigitalInOut(ROW_3)
row4 = digitalio.DigitalInOut(ROW_4)
row5 = digitalio.DigitalInOut(ROW_5)
row6 = digitalio.DigitalInOut(ROW_6)
row7 = digitalio.DigitalInOut(ROW_7)
row8 = digitalio.DigitalInOut(ROW_8)
row9 = digitalio.DigitalInOut(ROW_9)
row10 = digitalio.DigitalInOut(ROW_10)

rows = [row0,
        row1,
        row2,
        row3,
        row4,
        row5,
        row6,
        row7,
        row8,
        row9,
        row10]

for i in range(len(rows)):
    rows[i].direction = digitalio.Direction.OUTPUT
    rows[i].value = False

row0.direction = digitalio.Direction.OUTPUT
row0.value = False

validButtonNumbers = [0, 2, 5, 9, 14, 20,
                      1, 4, 8, 13,
                      3, 7,
                      6, 11, 17, 24,
                      10, 16, 23, 31, 40, 50,
                      15, 22, 30, 39, 49, 60,
                      21, 29, 38, 48, 59 , 71,
                      28, 37, 47, 58, 70,
                      36, 46, 57, 69, 82,
                      45, 56, 68, 81, 95,
                      55, 67, 80, 94, 109]

"""
def ButtonFunction(pushedButtonNumber):
    if pushedButtonNumber is 0:
        # code

    elif pushedButtonNumber is 2:
        # code

    elif pushedButtonNumber is 5:
        # code

    elif pushedButtonNumber is 9:
        # code

    elif pushedButtonNumber is 14:
        # code

    elif pushedButtonNumber is 20:
        # code

    elif pushedButtonNumber is 1:
        # code

    elif pushedButtonNumber is 4:
        # code

    elif pushedButtonNumber is 8:
        # code

    elif pushedButtonNumber is 16:
        # code

    elif pushedButtonNumber is 3:
        # code

    elif pushedButtonNumber is 7:
        # code

    elif pushedButtonNumber is 6:
        # code

    elif pushedButtonNumber is 11:
        # code

    elif pushedButtonNumber is 17:
        # code

    elif pushedButtonNumber is 24:
        # code

    elif pushedButtonNumber is 10:
        # code

    elif pushedButtonNumber is 16:
        # code

    elif pushedButtonNumber is 23:
        # code

    elif pushedButtonNumber is 31:
        # code

    elif pushedButtonNumber is 40:
        # code

    elif pushedButtonNumber is 50:
        # code

    elif pushedButtonNumber is 15:
        # code

    elif pushedButtonNumber is 22:
        # code

    elif pushedButtonNumber is 30:
        # code

    elif pushedButtonNumber is 39:
        # code

    elif pushedButtonNumber is 49:
        # code

    elif pushedButtonNumber is 60:
        # code

    elif pushedButtonNumber is 21:
        # code

    elif pushedButtonNumber is 29:
        # code

    elif pushedButtonNumber is 38:
        # code

    elif pushedButtonNumber is 48:
        # code

    elif pushedButtonNumber is 59:
        # code

    elif pushedButtonNumber is 71:
        # code

    elif pushedButtonNumber is 28:
        # code

    elif pushedButtonNumber is 37:
        # code

    elif pushedButtonNumber is 47:
        # code

    elif pushedButtonNumber is 58:
        # code

    elif pushedButtonNumber is 70:
        # code

    elif pushedButtonNumber is 36:
        # code

    elif pushedButtonNumber is 46:
        # code

    elif pushedButtonNumber is 57:
        # code

    elif pushedButtonNumber is 69:
        # code

    elif pushedButtonNumber is 82:
        # code

    elif pushedButtonNumber is 45:
        # code

    elif pushedButtonNumber is 56:
        # code

    elif pushedButtonNumber is 68:
        # code

    elif pushedButtonNumber is 81:
        # code

    elif pushedButtonNumber is 95:
        # code

    elif pushedButtonNumber is 55:
        # code

    elif pushedButtonNumber is 67:
        # code

    elif pushedButtonNumber is 80:
        # code

    elif pushedButtonNumber is 94:
        # code

    elif pushedButtonNumber is 109:
        # code

    else raise Exception("ruh-roh, something bad happened")
"""

def poll():
    pushedButton = -1

    # Continue polling button until a button is pressed
    while (pushedButton == -1):
        # Iterate over all rows
        for x in range(len(rows)):
            time.sleep(0.01)

            # Set pin high
            rows[i].value = True

            time.sleep(0.01)

            # Check if any pins are high
            if any(column.value is True for column in columns):
                # Iterate over columns to see which one
                for y in range(len(columns)):
                    if columns[i].value:
                        # Found which button it is, now log it and move on
                        pushedButton = ((x + y) * (x + y + 1) / 2) + y
                        break

            # Set pin back to low
            rows[i].value = False

    # Execute the button's function
    """ButtonFunction(pushedButton)"""

    # Wait for button to be released
    while any(column.value is True for column in columns):
        pass

