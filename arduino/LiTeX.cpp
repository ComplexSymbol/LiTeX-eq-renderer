#include <LiTeX.h>
#include <iostream>
#include <string> 
#include <vector>
#include "RenderEngine.h"

typedef unsigned long long ull;
typedef unsigned char ubyte;
//typedef char byte;

std::string Between(std::string str, ubyte start, char char1, char char2, bool quiet) {
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
            if (c1Count == c2Count) 
                return std::string(&str[c1Indx + 1], &str[i]);
            }
    }

    if (!quiet) {
        std::cerr << "\033[1;31m";
        std::cerr << "Could not find contents between " + std::string(1, char1) + " and " + std::string(1, char2) + " in " + str + "." << std::endl;
        std::cerr << "\033[0m";
    }
    throw new std::invalid_argument("");
}

ubyte lastFinishedBarHt = 0;
const std::string specials[5] = { "pi", "e", "im", "perm", "comb" };
Render GenerateRender(std::string eq, bool exp) {
    std::string lead = exp ? "^" : "";
    ubyte barHeight = 4;
    ubyte hang = 0;
    ubyte lastHeight = 0;

    Render render = Render(std::vector<ull>(), ubyte(10));

    for (ubyte i = 0; i < ubyte(eq.length()); i++) {
        // TRIVIAL CHARS ----------------------------------------------------------------------- TRIVIAL CHARS
        if (isdigit(eq[i]) || isalpha(eq[i]) || 
            eq[i] == '/' || eq[i] == '*' || eq[i] == '+' || eq[i] == '-' ||
            eq[i] == '`' || eq[i] == '~' || eq[i] == '.' || eq[i] == '='
        ) {
            Render gl = ReadGlyph(lead + eq[i]);
            render = AppendRenders(render, gl, barHeight);
            lastHeight = gl.height;
        }

        // PARENTHESIS AND ABS ----------------------------------------------------------- PARENTHESIS AND ABS
        else if (eq[i] == '(' || eq[i] == '[') {
            char pair[2] = { eq[i], eq[i] == '(' ? ')' : ']' };
            std::string contents = Between(eq, i, pair[0], pair[1]);
            i += ubyte(contents.size()) + 1;

            Render renderedConts = GenerateRender(contents, exp);
            byte resizeBy = max(0, renderedConts.height - (exp ? 7 : 10));

            // Opening parenthesis
            render = AppendRenders(render, 
                ReadGlyph(lead + std::string(1, pair[0]), -resizeBy, pair[0] == '[', exp), 
                barHeight, lastFinishedBarHt
            );
            barHeight = max(barHeight, lastFinishedBarHt);

            // Contents
            render = AppendRenders(render, renderedConts, barHeight, lastFinishedBarHt);
            
            // Closing parenthesis
            render = AppendRenders(render,
                ReadGlyph(lead + std::string(1, pair[1]), resizeBy, pair[0] == '[', exp),
                barHeight, lastFinishedBarHt
            );

            lastHeight = renderedConts.height;
        }

        // EXPONENTS AND SUBSCRIPT --------------------------------------------------- EXPONENTS AND SUBSCRIPT
        else if (eq[i] == '^' or eq[i] == '_') {
            bool isPower = eq[i] == '^';

            std::string contents = Between(eq, i, '{', '}');
            std::cout << "Found exponent with contents " << contents << std::endl;
            i += ubyte(contents.size()) + 2;

            Render renderedConts = GenerateRender(contents, true);

            if (isPower) {
                render = AppendRenders(render, renderedConts, 0, 0, exp ? 3 : 4, lastHeight + hang);
                lastHeight += renderedConts.height - (exp ? 3 : 4);
            }
            else {
                render = AppendRenders(render, renderedConts, barHeight, renderedConts.height - (exp ? 2 : 0));
                barHeight += max(0, renderedConts.height) - barHeight - (exp ? 2 : 0);
                hang += renderedConts.height - 4;
            }
        }
        
        // ESCAPE SEQUENCES ----------------------------------------------------------------- ESCAPE SEQUENCES
        else if (eq[i] == '\\') {
            std::string escSeq = "";
            try { escSeq = Between(eq, i, '\\', '{', true); } catch (...) { }
            
            // SPECIAL CHARS ----------------------------------- SPECIAL CHARS
            if (escSeq == "") {
                // Check if escape sequence is special character
                for (int spec = 0; spec < 5 /* Number of specials */; spec++) {
                    std::string attempt = "";
                    // If the special length exceedes the length of the string, substr will throw error
                    try { attempt = escSeq.substr(i + 1, specials[spec].size()); } catch (...) { continue; }
                    
                    // Found escape sequence that is a special character, append it
                    if (attempt == specials[spec]) {
                        escSeq = attempt;
                        Render gl = ReadGlyph(lead + escSeq);
                        render = AppendRenders(render, gl, barHeight);
                        lastHeight = gl.height;
                        break;
                    }
                }

                // No valid special was found
                if (escSeq == "") {
                    std::cerr << "\033[1;31m";
                    std::cerr << "Invalid escape sequence at '" << eq.substr(i) << "'" << std::endl;
                    std::cerr << "\033[0m";
                    throw new std::invalid_argument("");
                }
            }
            // FRACTIONS ------------------------------------------- FRACTIONS
            else if (escSeq == "frac") {
                std::cout << "Found fraction!" << std::endl;
                i += 5; // get index to first brace
                std::string numer = Between(eq, i, '{', '}');
                std::string denom = Between(eq, i + numer.size() + 2, '{', '}');
                i += numer.size() + 2 + denom.size() + 1; // pass expression

                Render rendNumer = GenerateRender(numer, true);
                Render rendDenom = GenerateRender(denom, true);
                // Positive shift means denom moves, negative shift means numer moves
                short shift = (rendNumer.bitmap.size() - rendDenom.bitmap.size()) / 2;

                Render fraction = Render(
                    std::vector<ull>(max(rendNumer.bitmap.size(), rendDenom.bitmap.size()) + 2), 
                    2 + rendNumer.height + rendDenom.height
                );
                fraction = MergeRenders(fraction, rendNumer, 1 - (shift < 0 ? shift : 0), rendDenom.height + 2);
                fraction = MergeRenders(fraction, rendDenom, 1 + (shift > 0 ? shift : 0), 0);
                
                Render bar = Render(std::vector<ull>(max(rendNumer.bitmap.size(), rendDenom.bitmap.size()) + 2, 1), 1);
                bar.bitmap[0] = 0;
                fraction = MergeRenders(fraction, bar, 0, rendDenom.height);
                
                render = AppendRenders(render, fraction, barHeight, rendDenom.height);
                barHeight = max(barHeight, rendDenom.height);
                lastHeight = rendNumer.height + rendDenom.height + 2;
            }
            // RADICALS -------------------------------------------- RADICALS
            else if (escSeq == "sqrt") {
                std::cout << "Found radical!" << std::endl;
                i += 5; // get index to first brace
                std::string index = Between(eq, i, '{', '}');
                std::string radicand = Between(eq, i + index.size() + 2, '{', '}');
                i += index.size() + 2 + radicand.size() + 1; // Pass expression

                Render rendIndex = GenerateRender(index, true);
                Render rendRadicand = GenerateRender(radicand);

                Render radical = Render(
                    std::vector<ull>(5 + rendIndex.bitmap.size() + rendRadicand.bitmap.size(), 0),
                    2 + rendRadicand.height + max(0, rendIndex.height + 2 - rendRadicand.height)
                );
                Render stem = Render(std::vector<ull>({
                    (1ull << (rendRadicand.height/2 + (rendRadicand.height % 2 != 0))) - 1,
                    ((1ull << (rendRadicand.height / 2)) - 1) << (rendRadicand.height / 2)
                }), radical.height - 1);

                // Place square root "hook"
                radical = MergeRenders(radical, ReadGlyph("rad"), rendIndex.bitmap.size() - 2, 0);
                // Place stem
                radical = MergeRenders(radical, stem, rendIndex.bitmap.size() + 1, 0);
                // Place bar 
                radical = MergeRenders(radical, Render(std::vector<ull>(rendRadicand.bitmap.size() + 3, 1ull), 1), rendIndex.bitmap.size() + 2, rendRadicand.height);
                // Place end marker
                radical = MergeRenders(radical, Render(std::vector<ull>(1, 0b11ull), 2), rendRadicand.bitmap.size() + rendIndex.bitmap.size() + 4, rendRadicand.height - 2);
                // Place index
                radical = MergeRenders(radical, rendIndex, 0, 4);
                // Place contents
                radical = MergeRenders(radical, rendRadicand, rendIndex.bitmap.size() + 3, 0);
                
                render = AppendRenders(render, radical, barHeight, lastFinishedBarHt);
                barHeight = max(barHeight, lastFinishedBarHt);
                lastHeight = radical.height + hang;
            }
        }
    }

    lastFinishedBarHt = barHeight;
    return render;
}
