#include "Evaluator.cpp"
#include <algorithm>

static void ReplaceAll(std::string &str, const std::string& from, const std::string& to) {
    size_t start_pos = 0;
    while((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // Handles case where 'to' is a substring of 'from'
    }
}

Render Graph(std::string eq, float scaleX = 0.125f, float scaleY = 0.125f) {
    Render graph = Render(std::vector<ull>(128, 4294967296ull), 64);
    graph.bitmap[64] = ULLONG_MAX;
    for (ubyte i = 1; i != 127; i++)
        if (i % 4 == 0)
            graph.bitmap[i] |= (i % 8 == 0 ? 0b11 : 0b1);
    graph.bitmap[0] |= 0x1111111111111110; 
    graph.bitmap[1] |= 0x0101010101010100;

    // Calculate values and plot
    std::string rEQ = eq;
    float y;
    ull prevY = 0;
    ull OR, nOR;
    for (sbyte i = 0; i != 127; i++) {
        ReplaceAll(rEQ, "x", "(" + CmplxToStr((i - 64) * scaleX) + ")");
        y = Evaluate(rEQ).real() * 1 / scaleY;

        std::cout << "Placing coordinate x: " << std::to_string((i - 64) * scaleX) << "... (" << (int)i << ", " << y << ")\n" << std::endl;
        OR = (0 <= y + 32 && y + 32 < 64) ? 1ull << (int)(y + 32) : 0;
        nOR = ~((OR << 1) | (OR >> 1));
        
        graph.bitmap[i] |= OR;
        graph.bitmap[i] &= nOR;
        graph.bitmap[max(0, i - 1)] &= nOR | prevY;
        graph.bitmap[min(126, i) + 1] &= nOR;

        rEQ = eq;
        prevY = OR;
    }

    return graph;
}