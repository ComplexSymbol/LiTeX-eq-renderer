#ifndef _LITEX_H
#define _LITEX_H
#include <Arduino.h>
#include <RenderEngine.h>

extern std::string Between(std::string str, ubyte start, char char1, char char2, bool reverse = false);
extern Render GenerateRender(std::string eq, bool exp = false);
 
#endif