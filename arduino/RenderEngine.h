#ifndef _RENDER_ENGINE_H
#define _RENDER_ENGINE_H
#include <Arduino.h>
#include <Prerendered.h>

typedef unsigned long long ull;
typedef unsigned char ubyte;
typedef signed char sbyte;

extern inline short max(short a, short b);
extern inline short min(short a, short b);

class Render {
    public:

    std::vector<ull> bitmap;
    ubyte height;

    Render(std::vector<ull> bmap, ubyte ht);
    void Print();
};
extern Render MergeRenders(Render a, Render b, ubyte x, ubyte y);
extern Render AppendRenders(Render a, Render b, ubyte aAlign = 0, ubyte bAlign = 0, ubyte overlap = 0, ubyte overlapFrom = 0);
extern Render ReadGlyph(std::string g, sbyte resizeParenBy = 0, bool absVal = false, bool isExp = false);

extern void SerialPrintlnString(std::string str);
extern std::string dtos(double dub);

#endif