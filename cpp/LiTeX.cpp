#include <iostream>
#include <string> 
#include <vector>
#include <chrono>
#include "RenderEngine.cpp"
#include "Prerendered.cpp"

typedef unsigned long long ull;
typedef unsigned char ubyte;
typedef char byte;

Render ReadGlyph(std::string g, ubyte resizeParenBy = 0, bool absVal = false, bool isExp = false) {
    std::vector<short> gl = prerenderedGlyphs.at(g);

    ubyte ht = gl[gl.size() - 1];
    gl.pop_back();

    if (resizeParenBy != 0) {
        short oldCol = gl[absVal ? 1 : (resizeParenBy < 0 ? 1 : (isExp ? 2 : 3))];
        short& refToCol = gl[absVal ? 1 : (resizeParenBy < 0 ? 1 : (isExp ? 2 : 3))];
        refToCol &= ~0b11uLL; // Mask out bottom bits for shifting.
        refToCol >>= resizeParenBy; // Shift to make room for expanded column
        refToCol |= (1ull << resizeParenBy) - 1; // Expand column
        refToCol &= ~0b11uLL; // Remove unused expanded column bits.
        refToCol |= oldCol & 0b11uLL; // Add old bits that were masked out.
    }

    std::vector<ull> cleanBitmap;
    cleanBitmap.reserve(gl.size());
    for (short val : gl) {
        cleanBitmap.push_back(static_cast<ull>(val) & 0xFFFFull); // mask to prevent junk
    }
    return Render(cleanBitmap, ht + resizeParenBy);
}

std::string Between(std::string str, ubyte start, char char1, char char2) {
    ubyte c1Indx = 0;
    ubyte c1Count = 0;
    ubyte c2Count = 0;

    for (ubyte i = start; i < ubyte(str.size()); i++) {
        if (str[i] == char1) {
            if (c1Count == 0) c1Indx = i;
            c1Count++;
        }
        else if (str[i] == char2) {
            c2Count++;
            if (c1Count == c2Count) return str.substr(c1Indx + 1, i - start -  2);
        }
    }

    throw new std::invalid_argument("Could not find contents between " + std::string(1, char1) + " and " + std::string(1, char2) + " in " + str + ".");
}

ubyte lastFinishedBarHt = 0;
Render GenerateRender(std::string eq, bool exp = false) {
    std::string lead = exp ? "^" : "";
    ubyte barHeight = 4;
    ubyte hang = 0;
    ubyte lastHeight = 0;

    Render render = Render(std::vector<ull>(), ubyte(10));

    for (ubyte i = 0; i < ubyte(eq.length()); i++) {
        if (isdigit(eq[i]) || isalpha(eq[i]) || 
            eq[i] == '/' || eq[i] == '*' || eq[i] == '+' || eq[i] == '-' ||
            eq[i] == '`' || eq[i] == '~' || eq[i] == '.' || eq[i] == '='
        ) {
            std::cout << eq[i] << std::endl;
            Render gl = ReadGlyph(lead + eq[i]);
            render = appendRenders(render, gl, barHeight);
            lastHeight = gl.height;
        }
        else if (eq[i] == '(' || eq[i] == '[') {
            char pair[2] = { eq[i], eq[i] == '(' ? ')' : ']' };
            std::string contents = Between(eq, i, pair[0], pair[1]);
            i += ubyte(contents.size()) + 1;

            Render renderedConts = GenerateRender(contents, exp);
            ubyte resizeBy = max(0, renderedConts.height - (exp ? 7 : 10));

            // Opening parenthesis
            render = appendRenders(render, 
                ReadGlyph(lead + std::string(1, pair[0]), -resizeBy, pair[0] == '[', exp), 
                barHeight, lastFinishedBarHt
            );
            barHeight = max(barHeight, lastFinishedBarHt);

            // Contents
            render = appendRenders(render, renderedConts, barHeight, lastFinishedBarHt);
            
            // Closing parenthesis
            render = appendRenders(render,
                ReadGlyph(lead + std::string(1, pair[1]), resizeBy, pair[0] == '[', exp),
                barHeight, lastFinishedBarHt
            );

            lastHeight = renderedConts.height;
        }
        else if (eq[i] == '^' or eq[i] == '_') {
            bool isPower = eq[i] == '^';

            std::string contents = Between(eq, i, '{', '}');
            std::cout << "Found exponent with contents " << contents << std::endl;
            i += ubyte(contents.size()) + 2;

            Render renderedConts = GenerateRender(contents, true);

            if (isPower)
                render = appendRenders(render, renderedConts, 0, 0, exp ? 3 : 4, lastHeight + hang);
            else {
                render = appendRenders(render, renderedConts, barHeight, renderedConts.height - (exp ? 2 : 0));
                barHeight += max(0, renderedConts.height) - barHeight - (exp ? 2 : 0);
                hang += renderedConts.height - 4;
            }
        }
    }

    lastFinishedBarHt = barHeight;
    return render;
}