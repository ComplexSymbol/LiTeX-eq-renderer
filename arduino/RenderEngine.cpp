#include "Prerendered.h"
#include <RenderEngine.h>
#include <vector>
#include <iostream>
#include <bitset>

typedef unsigned long long ull;
typedef unsigned char ubyte;
typedef signed char sbyte;

inline sbyte max(sbyte a, sbyte b) { return a > b ? a : b; }
inline sbyte min(sbyte a, sbyte b) { return a < b ? a : b; }

Render::Render(std::vector<ull> bmap, ubyte ht) {
    bitmap = bmap;
    height = ht;
}
void Render::Print(bool prettyPrint) {
    std::cout << "DIMENSIONS: " << bitmap.size() << "x" << (int)height << std::endl;
    
    for (ull col : bitmap) {
        if (col >> height) {
            std::cerr << "Warning: bitmap column contains bits outside declared height!" << std::endl;
            break;
        }
    }

    for (ubyte y = height; y > 0; y--) { // Print top to bottom
        for (unsigned short x = 0; x < bitmap.size(); x++) {
            if (prettyPrint) 
                std::cout << (((bitmap[x] >> (y - 1)) & 1) ? "██" : "  ");
            else 
                std::cout << (((bitmap[x] >> (y - 1)) & 1) ? "1" : "0");
        }
        std::cout << std::endl;
    }   
}

// Overlaps b over a at (x, y) and ORs all values.
// Original 'a' dimensions are returned. All values that do not overlap (hanging off) are ignored.
Render MergeRenders(Render a, Render b, ubyte x, ubyte y) {
    // Loop from x to min(x + b.bitmap.size, a.bitmap.size)

    // Why min? Because if x + b.bitmap.size > a.bitmap.size, 
    // then we get an index problem, this cuts off irrelevant b portions

    // Why not iterate from a to a.bitmap.size()? Because portions between 0 and x
    // aren't modified, so we don't have to loop over them.
    ull mask = (a.height >= 64) ? ~0ull : ((1ull << a.height) - 1ull); // careful if height == 64
    short stop = min(x + b.bitmap.size(), a.bitmap.size());

    for (short col = x; col < stop; col++) {
        a.bitmap[col] |= (b.bitmap[col - x] << min(63, y)) & mask;
    }

    return a;
}

// Appends b to a. Aligns aAlign and bAlign y values so they are on the same level.
// Returns a larger bitmap.
// `a` gets appended with `b` and (aligns `a` and `b` OR overlaps `b` by `overlap` starting at height `overlapFrom`)
Render AppendRenders(Render a, Render b, ubyte aAlign, ubyte bAlign, ubyte overlap, ubyte overlapFrom) {
    if (a.bitmap.empty())
        return b;
    
    // Half, rounded down, if they aren't set already.
    if (overlap == 0) {
        aAlign = aAlign == 0 ? ((a.height / 2) - 1) : aAlign;
        bAlign = bAlign == 0 ? ((b.height / 2) - 1) : bAlign;
    }

    // Positive diff means b has to move up to match a
    // Negative diff means a has to move up to match b
    sbyte diff = (sbyte)aAlign - bAlign;

    //std::cout << "AppendRenders ARGS: " 
    //    << "aAlign: " << (int)aAlign
    //    << ", bAlign: " << (int)bAlign
    //    << ", overlap: " << (int)overlap
    //    << ", overlapFrom: " << (int)overlapFrom
    //    << ", diff: " << (int)diff
    //    << std::endl;

    Render canvas = Render(
        std::vector<ull>(a.bitmap.size() + b.bitmap.size(), 0ull), // empty bitmap of a width + b width
        //Everything below sets height
        (overlap > 0) ? // Using overlap? 
        max(a.height, overlapFrom + b.height - overlap) : // Find the height when overlapping
        (a.height + max(((sbyte)aAlign - a.height) - ((sbyte)bAlign - b.height), 0) + max(-diff, 0)) // Find the height when aligned
                       // Possible unsigned math issue in the future`?
    );

    // Place in bottom left corner, move up if diff requires
    canvas = MergeRenders(canvas, a, 0, diff < 0 ? -diff : 0);

    // Place to the right of a, move up if diff requires OR if overlap requires
    canvas = MergeRenders(canvas, b, a.bitmap.size(), (overlap != 0) ? (overlapFrom - overlap) : (diff > 0 ? diff : 0));

    return canvas;
}

Render ReadGlyph(std::string g, sbyte resizeParenBy, bool absVal, bool isExp)
{
    std::vector<ushort> gl = prerenderedGlyphs.at(g);

    ubyte ht = gl[gl.size() - 1];
    gl.pop_back();

    if (resizeParenBy != 0) {
        ubyte indx = absVal ? 1 : (resizeParenBy < 0 ? 1 : (isExp ? 2 : 3));
        short oldCol = gl[indx];
        
        gl[indx] |= 0b11;
        gl[indx] <<= abs(resizeParenBy);
        gl[indx] |= oldCol;

        for (ubyte i = 0; i < gl.size(); i++) {
            if (i != indx) {
                oldCol = gl[i];
                gl[i] &= ushort(~0b11);
                gl[i] <<= abs(resizeParenBy);
                gl[i] |= oldCol & 0b11;
            }
        }
    }

    return Render(std::vector<ull>(gl.begin(), gl.end()), ht + abs(resizeParenBy));
}
