#include "Evaluator.cpp"
#include <algorithm>

std::string ReplaceAll(std::string str, const std::string from, const std::string to) {
    size_t start_pos = 0;
    while((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // Handles case where 'to' is a substring of 'from'
    }
    return str;
}

void MaskedOr(Render &render, ull toOR, sbyte index, bool rightOnly = false) {
    if (index < 0) return;

    if (index != 0 && !rightOnly) {
        render.bitmap[index - 1] &= ~(toOR << 1);
        render.bitmap[index - 1] &= ~toOR;
        render.bitmap[index - 1] &= ~(toOR >> 1);
    }

    if (index != render.bitmap.size() - 1) {
        render.bitmap[index + 1] &= ~(toOR << 1);
        render.bitmap[index + 1] &= ~toOR;
        render.bitmap[index + 1] &= ~(toOR >> 1);
    }

    render.bitmap[index] &= ~(toOR << 1);
    render.bitmap[index] &= ~(toOR >> 1);
    render.bitmap[index] |= toOR;
}

Render Graph(std::string eq, float scaleX = 0.125f, float scaleY = 0.125f, bool showScale = false, sbyte traceX = -1) {
    Render graph = Render(std::vector<ull>(128, 4294967296ull), 64);
    Render coord = Render(std::vector<ull>({ 0 }), 1);

    graph.bitmap[64] = ULLONG_MAX;
    for (ubyte i = 1; i != 127; i++)
        if (i % 4 == 0)
            graph.bitmap[i] |= (i % 8 == 0 ? 0b11 : 0b1);
    graph.bitmap[0] |= 0x1111111111111110;
    graph.bitmap[1] |= 0x0101010101010100;

    if (showScale) {
        ubyte pos = 80; 
        graph.bitmap[pos] |= 0b111000;
        for (ubyte i = pos; i < pos + 8; i++)
            graph.bitmap[i] |= 0b010000;
        graph.bitmap[pos + 8] |= 0b111000;
        
        Render scale = GenerateRender(CmplxToStr(scaleX * 8), true);
        graph = MergeRenders(graph, scale, pos + 4 - (scale.bitmap.size() / 2), 7);
    }
    float traceY = NaN.real();
    if (traceX >= 0) {
        cmplx traceEval = Evaluate(ReplaceAll(eq, "x", "(" + CmplxToStr((traceX - 64) * scaleX) + ")"));
        if (traceEval.imag() > 0.001L) { traceEval = NaN; } 
        
        coord = GenerateRender(ReplaceAll("(" + CmplxToStr((traceX - 64) * scaleX, 3) + "," + CmplxToStr(traceEval.real(), 3) + ")", "-", "~"), true);
        
        if (coord.bitmap.size() >= 63)
            graph.bitmap[64] &= ULLONG_MAX >> 8;
    }

    // Calculate values and plot
    float y = 0;
    ull ybmap = 0, prevYbmap = 0, traceYbmap = 0;
    cmplx eval = 0;
    for (sbyte i = 0; i <= 126; i++) {
        eval = Evaluate(ReplaceAll(eq, "x", "(" + CmplxToStr((i - 64) * scaleX) + ")"));
        if (std::abs(eval.imag()) > 0.001L) { 
            std::cout << "Imaginary portion too large: " << CmplxToStr(eval) << std::endl;
            prevYbmap = 0; 
            continue;  
        }
        
        y = std::round(eval.real() * (1 / scaleY));
        ybmap = (-29 <= y && y < 32) ? 1ull << ((int)y + 32) : 0;
        
        if (i == traceX && !isNan(eval)) traceY = y;
        if ((i >= graph.bitmap.size() - coord.bitmap.size() - 1) && y >= 25) { prevYbmap = 0; continue; }

        //std::cout << "Placing coordinate (" << (int)(i - 64) << ", " << y << ")  bmap: " << ybmap << std::endl;
        MaskedOr(graph, ybmap, i, false);
        if (i > 0 && ybmap != 0)
            graph.bitmap[i - 1] |= prevYbmap;

        prevYbmap = ybmap;
    }

    if (traceX >= 0) {
        ull traceYbmap = (-29 <= traceY && traceY < 32) ? 1ull << ((int)traceY + 32) : 0;
        if (isNan(traceY)){
            MaskedOr(graph, 0x280000000, traceX - 1, false);
            MaskedOr(graph, 0x100000000, traceX, true);
            MaskedOr(graph, 0x280000000, traceX + 1, true);
        }
        else if (-29 <= traceY && traceY < 32 && !(traceX >= 127 - coord.bitmap.size() && traceY >= 23)) {
            // Outline point on graph
            MaskedOr(graph, (traceYbmap << 1) | traceYbmap | (traceYbmap >> 1), traceX - 2, false);
            MaskedOr(graph, traceYbmap << 2, traceX - 1, true);
            MaskedOr(graph, traceYbmap >> 2, traceX - 1, true);
            MaskedOr(graph, traceYbmap << 2, traceX, true);
            MaskedOr(graph, traceYbmap >> 2, traceX, true);
            MaskedOr(graph, traceYbmap << 2, traceX + 1, true);
            MaskedOr(graph, traceYbmap >> 2, traceX + 1, true);
            MaskedOr(graph, (traceYbmap << 1) | traceYbmap | (traceYbmap >> 1), traceX + 2, true);
            MaskedOr(graph, traceYbmap, traceX);
        }
        else if (-29 > traceY) {
            MaskedOr(graph, 0x2, traceX - 1, false);
            MaskedOr(graph, 0xF, traceX, true);
            MaskedOr(graph, 0x2, traceX + 1, true);
        } 
        else if (!(traceX >= 127 - coord.bitmap.size() && traceY >= 23)) {
            MaskedOr(graph, 0x4000000000000000, traceX - 1, false);
            MaskedOr(graph, 0xF000000000000000, traceX, true);
            if (traceX > 0)
                graph.bitmap[traceX - 1] |= 0x4000000000000000;
            MaskedOr(graph, 0x4000000000000000, traceX + 1, true);
        }
        else if (traceX >= 127 - coord.bitmap.size() && traceY >= 23) {
            MaskedOr(graph, 0x80000000000000, traceX - 1, false);
            MaskedOr(graph, 0x1E0000000000000, traceX, true);
            if (traceX > 0)
                graph.bitmap[traceX - 1] |= 0x80000000000000;
            MaskedOr(graph, 0x80000000000000, traceX + 1, true);
        }
        
        graph = MergeRenders(graph, coord, 127 - coord.bitmap.size(), 58);
    }

    return graph;
}