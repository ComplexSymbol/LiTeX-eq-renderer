#ifndef _DISPLAY_SPI_H
#define _DISPLAY_SPI_H
#include <Arduino.h>

typedef unsigned char ubyte;

// Declare pinouts
extern const ubyte CS_PIN;
extern const ubyte DC_PIN;
extern const ubyte RST_PIN;
extern const ubyte SCK_PIN;
extern const ubyte MOSI_PIN;

// Command constants:
extern const ubyte BIAS_SEL;
extern const ubyte SEG_DIR;
extern const ubyte COM_DIR;

extern const ubyte REG_RATIO;
extern const ubyte ELEC_VOL1;
extern const ubyte ELEC_VOL2;

extern const ubyte PWR_CTL;
extern const ubyte DISP_ON;
extern const ubyte DISP_OFF;

extern const ubyte SFTWR_RST;

extern const ubyte INVR_ON;
extern const ubyte INVR_OFF;

// Data constants
extern const ubyte STRT_LINE;
extern const ubyte PAGE_ADDR;
extern const ubyte CLMN_ADR1;
extern const ubyte CLMN_ADR2;

extern void send_data(ubyte data);
extern void send_command(ubyte command);

extern void setup_SPI();
extern void kill_SPI();
extern void hardware_reset();
extern void initialize_display();
extern void adjust_contrast(ubyte val);
extern void software_reset();
extern void clear_display();
extern void send_render(Render render, ubyte k = 0);

#endif