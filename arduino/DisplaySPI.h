#ifndef _RENDER_ENGINE_H
#define _RENDER_ENGINE_H
#include <Arduino.h>

typedef unsigned char ubyte;

extern void SendData(ubyte data);
extern void SendCommand(ubyte command);

extern void hardware_reset();
extern void initialize_display();
extern void adjust_contrast(ubyte val);
extern void software_reset();
extern void clear_display();

#endif