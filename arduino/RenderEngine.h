#ifndef _RENDER_ENGINE_H
#define _RENDER_ENGINE_H
#include <Arduino.h>
#include <string>

extern inline char max(char a, char b);
extern inline char min(char a, char b);

class Render {
    public:

    std::vector<unsigned long long> bitmap;
    unsigned char height;

    Render(std::vector<unsigned long long> bmap, unsigned char ht);
    void Print(bool prettyPrint = false);
};
extern Render MergeRenders(Render a, Render b, unsigned char x, unsigned char y);
extern Render AppendRenders(Render a, Render b, unsigned char aAlign = 0, unsigned char bAlign = 0, unsigned char overlap = 0, unsigned char overlapFrom = 0);
extern Render ReadGlyph(std::string g, byte resizeParenBy = 0, bool absVal = false, bool isExp = false);


#endif