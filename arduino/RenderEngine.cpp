#include <RenderEngine.h>

typedef unsigned long long ull;
typedef unsigned char ubyte;
typedef signed char sbyte;

inline short max(short a, short b) { return a > b ? a : b; }
inline short min(short a, short b) { return a < b ? a : b; }

static const std::map<ubyte, std::string> printGlyphs = {
    { 0b00, " " },
    { 0b01, "▄" },
    { 0b10, "▀" },
    { 0b11, "█" }
};

Render::Render(std::vector<ull> bmap, ubyte ht) {
    bitmap = bmap;
    height = ht;
};

void Render::Print() {
    SerialPrintlnString("DIMENSIONS: " + std::to_string(bitmap.size()) + "x" + std::to_string(height));
    for (ubyte y = height; y > 0; y -= 2) { // Print top to bottom
        for (ushort x = 0; x < bitmap.size(); x++) {
            ubyte key = (bitmap[x] >> (y - 2)) & 0b11;
            Serial.print(printGlyphs.at(key).c_str());
        }
        
        SerialPrintlnString("");
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
    if (a.bitmap.empty()) {
        return b;
    }
    
    // Half, rounded down, if they aren't set already.
    if (overlap == 0) {
        aAlign = aAlign == 0 ? ((a.height / 2) - 1) : aAlign;
        bAlign = bAlign == 0 ? ((b.height / 2) - 1) : bAlign;
    }

    // Positive diff means b has to move up to match a
    // Negative diff means a has to move up to match b
    sbyte diff = aAlign - bAlign;

    SerialPrintlnString("AppendRenders ARGS: aAlign:" + std::to_string(int(aAlign))
        + ", bAlign: " + std::to_string(int(bAlign))
        + ", overlap: " + std::to_string(int(overlap))
        + ", overlapFrom: " + std::to_string(int(overlapFrom))
        + ", diff: " + std::to_string(int(diff))
       );

    Render canvas = Render(
        std::vector<ull>(a.bitmap.size() + b.bitmap.size(), 0ull), // empty bitmap of a width + b width
        //Everything below sets height
        (overlap > 0) ? // Using overlap? 
        max(a.height, overlapFrom + b.height - overlap) : // Find the height when overlapping
        (a.height + max((aAlign - a.height) - (bAlign - b.height), 0) + max(-diff, 0)) // Find the height when aligned
                       // Possible unsigned math issue in the future?
    );

    // Place in bottom left corner, move up if diff requires
    canvas = MergeRenders(canvas, a, 0, diff < 0 ? -diff : 0);

    // Place to the right of a, move up if diff requires OR if overlap requires
    canvas = MergeRenders(canvas, b, a.bitmap.size(), (overlap != 0) ? (overlapFrom - overlap) : (diff > 0 ? diff : 0));

    return canvas;
}

Render ReadGlyph(std::string g, sbyte resizeParenBy, bool absVal, bool isExp) {
    SerialPrintlnString("    Reading glyph...");
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

    SerialPrintlnString("Done");
    return Render(std::vector<ull>(gl.begin(), gl.end()), ht + abs(resizeParenBy));
}

void SerialPrintlnString(std::string str) {
    Serial.println(str.c_str());
}

std::string dtos(double dub) {
    char buffer[24];
    dtostrf(dub, 0, 4, buffer); // double, width, precision, buffer
    
    return buffer;
}