#include <SPI.h>
#include "DisplaySPI.h"

typedef unsigned char ubyte;

// Declare pinouts
const ubyte CS_PIN = 10;
const ubyte DC_PIN = 14;
const ubyte RST_PIN = 9;
const ubyte SCK_PIN = 13;
const ubyte MOSI_PIN = 11;

// Command constants:
const ubyte BIAS_SEL = 0b10100010;
const ubyte SEG_DIR = 0b10100000;
const ubyte COM_DIR = 0b11000000;

const ubyte REG_RATIO = 0b00100000;
const ubyte ELEC_VOL1 = 0b10000001;
const ubyte ELEC_VOL2 = 0b00000000;

const ubyte PWR_CTL = 0b00101000;
const ubyte DISP_ON = 0b10101111;
const ubyte DISP_OFF = 0b10101110;

const ubyte SFTWR_RST = 0b11100010;

const ubyte INVR_ON = 0b10100111;
const ubyte INVR_OFF = 0b10100110;

// Data constants
const ubyte STRT_LINE = 0b01000000;
const ubyte PAGE_ADDR = 0b10110000;
const ubyte CLMN_ADR1 = 0b00010000;
const ubyte CLMN_ADR2 = 0b00000000;

void send_data(ubyte data) {
    // gain control of the SPI port
    // and configure settings
    SPI.beginTransaction(SPISettings(100'000, MSBFIRST, SPI_MODE0));
        // data mode
        digitalWrite(DC_PIN, HIGH);
        // take the SS pin low to select the chip:
        digitalWrite(CS_PIN, LOW);
        //  send in the address and value via SPI:
        SPI.transfer(data);
        // take the SS pin high to de-select the chip:
        digitalWrite(CS_PIN,HIGH);
        // release control of the SPI port
    SPI.endTransaction();
}

void send_command(ubyte command) {
    SPI.beginTransaction(SPISettings(100'000, MSBFIRST, SPI_MODE0));
        // command mode
        digitalWrite(DC_PIN, LOW);

        digitalWrite(CS_PIN, LOW);
        SPI.transfer(command);
        digitalWrite(CS_PIN,HIGH);
    SPI.endTransaction();
}

void hardware_reset() {
    digitalWrite(RST_PIN, LOW);
    delay(100);

    digitalWrite(RST_PIN, HIGH);
    delay(100);
}

void initialize_display() {
    hardware_reset();

    send_command(BIAS_SEL | 0b00000000);  // Bias select (1/7)
    send_command(SEG_DIR | 0b00000001);  // Normal SEG direction
    send_command(COM_DIR | 0b00000000);  // Normal COM direction

    send_command(REG_RATIO | 0b00000111);  // 111 (7) Reg Ratio
    send_command(ELEC_VOL1);
    send_command(ELEC_VOL2 | 0b00011111);  // Middle (0x1F) electronic volume

    send_command(PWR_CTL | 0b00000111); // Power control
    send_command(DISP_ON);
}

void adjust_contrast(ubyte val) {
    if (val > 63)
        val = 63;

    send_command(ELEC_VOL1);
    send_command(ELEC_VOL2 | val);
}

void software_reset() {
    send_command(SFTWR_RST);
    adjust_contrast(0x28);
    send_command(STRT_LINE | 0x00);
}

void clear_display() {
    send_command(STRT_LINE | 0x00);
    send_command(PAGE_ADDR | 0x00);

    for (ubyte y = 0; y < 8; y++) {
        send_command(PAGE_ADDR | y);

        send_command(CLMN_ADR1 | 0x00);
        send_command(CLMN_ADR2 | 0x00);

        for (ubyte x = 0; x < 132; x++)
            send_data(0x00);
    }
}