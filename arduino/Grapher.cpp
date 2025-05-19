#include <Grapher.h>
#include <Evaluator.h>
#include <RenderEngine.h>
#include <string>
#include <iostream>

static void ReplaceAll(std::string &str, const std::string& from, const std::string& to) {
    size_t start_pos = 0;
    while((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // Handles case where 'to' is a substring of 'from'
    }
}

Render Graph(std::string eq, float scaleX, float scaleY) {
    Render graph = Render(std::vector<ull>(128, 4294967296ull), 64);
    graph.bitmap[64] = 0xFFFF'FFFF'FFFF'FFFF;
    for (ubyte i = 1; i != 127; i++)
        if (i % 4 == 0)
            graph.bitmap[i] |= (i % 8 == 0 ? 0b11 : 0b1);
    graph.bitmap[0] |= 0x1111111111111110; 
    graph.bitmap[1] |= 0x0101010101010100;

    // Calculate values and plot
    std::string rEQ = eq;
    float y = 0;
    ull ybmap = 0, mask = 0, prevYbmap;
    cmplx eval;
    for (sbyte i = 0; i != 127; i++) {
        ReplaceAll(rEQ, "x", "(" + CmplxToStr((i - 64) * scaleX) + ")");
        eval = Evaluate(rEQ);
        if (std::abs(eval.imag()) > 0.001L) { rEQ = eq; continue; }
        
        y = std::round(eval.real() * (1 / scaleY));
        ybmap = (-29 <= y && y < 32) ? 1ull << ((int)y + 32) : 0;
        
        mask = ~((ybmap << 1) | ybmap | (ybmap >> 1));
        std::cout << "Placing coordinate (" << (int)(i - 64) << ", " << y << ")  bmap: " << ybmap << std::endl;
        
        graph.bitmap[i] &= mask;
        graph.bitmap[i] |= ybmap;
        graph.bitmap[max(0, i - 1)] &= mask | prevYbmap;
        graph.bitmap[min(126, i) + 1] &= mask;

        prevYbmap = ybmap;
        rEQ = eq;
    }

    return graph;
}