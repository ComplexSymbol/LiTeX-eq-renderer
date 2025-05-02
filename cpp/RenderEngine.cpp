#include <vector>
#include <iostream>
#include <bitset>

typedef unsigned long long ull;
typedef unsigned char ubyte;
typedef char byte;

inline byte max(byte a, byte b) { return a > b ? a : b; }
inline byte min(byte a, byte b) { return a < b ? a : b; }

class Render {
    public:
    
    std::vector<ull> bitmap;
    ubyte height;

    Render(std::vector<ull> bmap, ubyte ht) {
        bitmap = bmap;
        height = ht;
    }

    void Print(bool prettyPrint=false) {
        std::cout << "DIMENSIONS: " << bitmap.size() << "x" << int(height) << std::endl;
        
        for (ull col : bitmap) {
            if (col >> height) {
                std::cerr << "Warning: bitmap column contains bits outside declared height!" << std::endl;
                break;
            }
        }

        for (ubyte y = height; y > 0; y--) { // Print top to bottom
            for (ubyte x = 0; x < ubyte(bitmap.size()); x++) {
                if (prettyPrint) 
                    std::cout << (((bitmap[x] >> (y - 1)) & 1) ? "██" : "  ");
                else 
                    std::cout << (((bitmap[x] >> (y - 1)) & 1) ? "1" : "0");
            }
            std::cout << std::endl;
        }   
    }
};

// Overlaps b over a at (x, y) and ORs all values.
// Original 'a' dimensions are returned. All values that do not overlap (hanging off) are ignored.
Render mergeRenders(Render a, Render b, ubyte x, ubyte y) {
    // Loop from x to min(x + b.bitmap.size, a.bitmap.size)

    // Why min? Because if x + b.bitmap.size > a.bitmap.size, 
    // then we get an index problem, this cuts off irrelevant b portions

    // Why not iterate from a to a.bitmap.size()? Because portions between 0 and x
    // aren't modified, so we don't have to loop over them.
    ull mask = (a.height >= 64) ? ~0ull : ((1ull << a.height) - 1ull); // careful if height == 64
    ubyte stop = min(x + b.bitmap.size(), a.bitmap.size());

    for (ubyte col = x; col < stop; col++) {
        a.bitmap[col] |= (b.bitmap[col - x] << min(63, y)) & mask;
    }

    return a;
}

// Appends b to a. Aligns aAlign and bAlign y values so they are on the same level.
// Returns a larger bitmap.
// `a` gets appended with `b` and (aligns `a` and `b` OR overlaps `b` by `overlap` starting at height `overlapFrom`)
Render appendRenders(Render a, Render b, ubyte aAlign = 0, ubyte bAlign = 0, ubyte overlap = 0, ubyte overlapFrom = 0) {
    if (a.bitmap.empty()) {
        return b;
    }
    
    // Half, rounded down, if they aren't set already.
    if (overlap != 0) {
        aAlign = aAlign == 0 ? b.height / 2 - 1 : aAlign;
        bAlign = bAlign == 0 ? b.height / 2 - 1 : bAlign;
    }
    
    // Positive diff means b has to move up to match a
    // Negative diff means a has to move up to match b
    byte diff = aAlign - bAlign;

    Render canvas = Render(
        std::vector<ull>(a.bitmap.size() + b.bitmap.size(), 0ull), // empty bitmap of a width + b width
        //Everything below sets height
        (overlap > 0) ? // Using overlap? 
        max(a.height, overlapFrom + b.height - overlap) : // Find the height when overlapping
        (a.height + max((aAlign - a.height) - (bAlign - b.height), 0) + max(-diff, 0)) // Find the height when aligned
                       // Possible unsigned math issue in the future?
    );

    // Place in bottom left corner, move up if diff requires
    canvas = mergeRenders(canvas, a, 0, diff < 0 ? -diff : 0);

    // Place to the right of a, move up if diff requires OR if overlap requires
    canvas = mergeRenders(canvas, b, a.bitmap.size(), (overlap != 0) ? (overlapFrom - overlap) : (diff > 0 ? diff : 0));

    return canvas;
}