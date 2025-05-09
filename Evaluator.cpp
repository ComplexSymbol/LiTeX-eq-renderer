#include <iostream>
#include <cmath>
#include <complex>
#include <string>
#include <vector>
#include <sstream>
#include <iomanip>
#include <map>
#include "LiTeX.cpp"

typedef unsigned char ubyte;
typedef signed char sbyte;
typedef std::complex<double> cmplx;

const cmplx NaN(std::nan("0"), std::nan("0"));
inline bool isNan(cmplx z) { return z != z; }

sbyte sgn(double val) {
    return (0 < val) - (val < 0);
}

inline std::string CmplxToStr(cmplx z, ubyte prec = 10) {
    return (z.imag() == 0 || z.real() == 0)
         ? (std::stringstream() << std::setprecision(prec) << (z.imag() == 0 ? z.real() : z.imag()) << (z.imag() == 0 ? "" : "i")).str()
         : ("(" + (std::stringstream() << std::setprecision(prec) << z.real()).str() + (sgn(z.imag()) >= 0 ? "+" : "") + (std::stringstream() << z.imag()).str() + "i)");
}

// PARSE COMPLEX ===================================================================== PARSE COMPLEX
cmplx ParseComplex(std::string str) {
    double real = 0;
    double imag = 0;
    ubyte start = 0;
    std::string reason = "";

PARSE_START:
    ubyte stop = str.size() - (str[str.size() - 1] == ')' ? 1 : 0);
    start += (str[0] == '(' && start == 0 ? 1 : 0);
    for (ubyte i = start; i < stop; i++) {
        if (i == start && str[i] == '-') continue;
        
        // We found the end of a number! (Or the string ended (or it's just part of sci notation))
        bool isEnd = i == stop - 1;
        if (str[i] == '-' || str[i] == '+' || isEnd) {
            if (str[i - 1] == 'e') {
                continue; // It's fine guys. Don't worry about the exponent
            }
            
            if (str[i - (isEnd ? 0 : 1)] == 'i') {
                if (imag != 0) {
                    reason = "Multiple imaginary parts found";
                    goto ERROR; // Woah, we already found imag part
                }

                imag = std::stod(str.substr(start, i - start + (isEnd ? 0 : -1)));
                break; // Let's get out of here
            }
            else {
                if (real != 0) {
                    reason = "Multiple real parts found";
                    goto ERROR; // Woah, we already found real part
                }

                real = std::stod(str.substr(start, i - start + (isEnd ? 1 : 0)));
                start = i + (str[i] == '+' ? 1 : 0);
                
                if (!(i == str.size() - 1))
                    goto PARSE_START; // Restart parsing cuz there still might be imag part
                break;
            }
        }

        if (!(isdigit(str[i]) || str[i] == 'e' || str[i] == '.')) {
            reason = "Unrecongized character " + std::string(1, str[i]);
            goto ERROR;
        }
    }

    if (real != 0 && imag != 0 && 
        (str[0] != '(' && str[str.size() - 1] != ')')
    ) {
        reason = "Complex numbers must be surrounded by parenthesis";
        goto ERROR;
    }

    return cmplx(real, imag);
    
ERROR:
    std::cerr << "                                                    >>> COULD NOT PARSE '" << str << "' FOR COMPLEX (" << reason << ")" << std::endl;
    return NaN;
}

// FIND COMPLEX ====================================================================== FIND COMPLEX
// Avoid slicing and checking with ParseComplex, which is slow
// Returns complex-parseable string.
std::string FindCmplx(std::string str, ubyte loc, bool before) {
    ubyte minusCount = 0;
    ubyte plusCount = 0;
    for (ubyte i = loc + (before ? -1 : 1); 
        before ? (i >= 0) : (i < str.size()); 
        i += (before ? -1 : 1)
    ) {
        if (i == loc - 1 && before && str[i] == ')') {
            // Found true complex, return contents
            return "(" + Between(str, i, ')', '(', true) + ")";
        }
        else if (!before && i == loc + 1 && str[i] == '(')
            return "(" + Between(str, i, '(', ')') + ")";

        if (str[i] == '+') // Must be part of exp
            if (str[i - 1] != 'e' || plusCount != 0)
                goto ERROR;
            else 
                plusCount++;
        
        else if (str[i] == '-') { // Found minus, could be negative or e-...
            if (!before) {
                if (i == loc + 1) {
                    minusCount++;
                }
                else if (str[i - 1] != 'e' || minusCount > 1)
                    return str.substr(loc + 1, i - loc - 1);
            }
            else {
                if (str[i - 1] == 'e' && minusCount == 0)
                minusCount++; // Increase minus count
                else if (minusCount == 1) // Negative number
                    return str.substr(i, loc - i);
                else
                    goto ERROR;
            }
        }
        else if (str[i] == 'e' && (!(str[i + 1] == '+' || str[i + 1] == '-') || !isdigit(str[i + 2])))
            goto ERROR;
        // Encountered unidentified character, must be end of number
        else if (!(isdigit(str[i]) || str[i] == 'e' || str[i] == '.' || (str[i] == 'i' && before && i == loc - 1)) || i == (before ? 0 : str.size() - 1))
            return before ? str.substr(i, loc - i) : str.substr(loc + 1, i - loc);
    }

ERROR:
    std::cerr << "                                                    >>> COULD NOT FIND COMPLEX" << std::endl;
    return "";
}

// ADD IMP MULT ====================================================================== ADD IMP MULT
void AddImpMultTo(std::string& eq) {
    for (ubyte i = 1; i < eq.size() - 1; i++) {
        if ((isdigit(eq[i]) && eq[i + 1] == '\\') || // 5\pi
            (isdigit(eq[i]) && eq[i + 1] == '(') || // 2(3...
            (isdigit(eq[i]) && isalpha(eq[i + 1]) 
                && eq[i + 1] != 'e' && eq[i + 1] != 'i') || // 9sin... but not 3e+... or 3i...
            (isalpha(eq[i]) && isdigit(eq[i + 1])) || // \pi3...
            (isalpha(eq[i]) && eq[i + 1] == '\\') || // \pi\e...
            (eq[i] == ')' && eq[i + 1] == '\\') || // ...4)\pi
            (eq[i] == ')' && eq[i + 1] == '(') || // ...3)(6...
            (eq[i] == ')' && isdigit(eq[i + 1])) || // ...)7
            (eq[i] == ')' && isalpha(eq[i + 1])) || // ...)x...
            (eq[i] == '}' && isdigit(eq[i + 1]))) // ...2}7
        eq.insert(i + 1, 1, '*');
    }
}

const std::unordered_map<std::string, ubyte> trigMap = {
    { "sin", 1 },
    { "cos", 2 },
    { "tan", 3 },
    { "sec", 4 },
    { "csc", 5 },
    { "cot", 6 },
    { "sin^{-1}", 7 },
    { "cos^{-1}", 8 },
    { "tan^{-1}", 9 },
};
auto operateTrig = [](std::string func, cmplx n) {
    switch (trigMap.at(func)) {
        case 1: return sin(n);
        case 2: return cos(n);
        case 3: return tan(n);
        case 4: return cmplx(1,0) / sin(n);
        case 5: return cmplx(1,0) / cos(n);
        case 6: return cmplx(1,0) / tan(n);
        case 7: return asin(n);
        case 8: return acos(n);
        case 9: return atan(n);
    }
    return NaN;
};
auto operate = [](ubyte op, cmplx a, cmplx b) {
    switch (op) {
        case 0: return a / b;
        case 1: return a * b;
        case 2: return a - b;
        case 3: return a + b;
    }
    return NaN;
};

// FIND TRIGS ======================================================================== FIND TRIGS
std::tuple<std::string, ubyte> FindTrigs(std::string eq, std::array<std::string, 9> trigs) {
    for (ubyte i = 0; i < size(eq); i++) {
        for (ubyte n = 0; n < trigs.size(); n++) {
            if (eq.substr(i, trigs[n].size()) == trigs[n])
                return std::tuple<std::string, ubyte>(trigs[n], i);
        }
    }
    std::cerr << "                                                    >>> COULD NOT FIND TRIG IN EQ: '" << eq << "'" << std::endl;
    return std::tuple<std::string, ubyte>("", 0xFF);
}

// EVALUATE ========================================================================== EVALUATE
cmplx Evaluate(std::string eq) {
    std::string reason = "";
{ // Scope so goto ERROR will not bypass variable initialization
    
    // SETUP EQUATION ==================================================== SETUP EQUATION
    {   cmplx test; // Is eq a number? (Scope so test is del)
        std::cout << "Testing whether eq is complex..." << std::endl;
        if (!isNan(test = ParseComplex(eq))) return test;   }

    AddImpMultTo(eq);
    
    // ` is placeholder character for renderer.
    if (eq.find('`') != std::string::npos) { reason = "Equation has placeholders"; goto ERROR; }
    
 /* TRIGONOMETRIC FUNCTIONS */ {
        std::cout << "Finding trig functions..." << std::endl;
        std::tuple<std::string, ubyte> loc;
        while((loc = FindTrigs(eq, std::array<std::string, 9>({ "sin", "cos", "tan", "sec", "csc", "cot", "sin^{-1}", "cos^{-1}", "tan^{-1}" })))
            != std::tuple<std::string, ubyte>("", 0xFF)
        ) {
            std::cout << "Found trig function " << std::get<0>(loc) << std::endl;
            std::string contents = Between(eq, std::get<1>(loc) + std::get<0>(loc).size(), '(', ')');
            
            eq.erase(std::get<1>(loc), std::get<0>(loc).size() + contents.size() + 2);
            eq.insert(std::get<1>(loc), CmplxToStr(operateTrig(std::get<0>(loc), Evaluate(contents))));
        }
    } // Scope so loc is freed. (I want to change type of loc from tuple -> size_t)

    // LOGARITHMS
    size_t loc = -1;
    while((loc = eq.find('log')) != std::string::npos) {
        std::string base = Between(eq, loc + 4, '{', '}');
        std::string contents = Between(eq, loc + base.size() + 6, '(', ')');

        eq.erase(loc, base.size() + contents.size() + 8);
        eq.insert(loc, CmplxToStr(log(Evaluate(contents)) / log(Evaluate(base))));
        // Use change-of-base formula (inefficient, but too lazy to write my own variable base thing)
    }

    // PARENTHESIS
    loc = -1;
    while ((loc = eq.find('(', loc + 1)) != std::string::npos) {
        std::string contents = Between(eq, loc, '(', ')');
        std::cout << "Found parenthesis with contents: " << contents << std::endl;
        
        cmplx toRepl = ParseComplex("(" + contents + ")");
        if (isNan(toRepl)) toRepl = Evaluate(contents);

        eq.erase(loc, contents.size() + 2);
        eq.insert(loc, CmplxToStr(toRepl));
    }
    
    // RADICALS
    loc = -1;
    while ((loc = eq.find("\\sqrt", loc + 1)) != std::string::npos) {
        std::string nth = Between(eq, loc + 5, '{', '}');
        std::string root = Between(eq, loc + 7 + nth.size(), '{', '}');

        eq.erase(loc, nth.size() + 7 + root.size());
        eq.insert(loc, CmplxToStr(pow(Evaluate(root), cmplx(1, 0) / Evaluate(nth))));
    }

    // FRACTIONS
    loc = -1;
    while ((loc = eq.find("\\frac", loc + 1)) != std::string::npos) {
        std::string numer = Between(eq, loc + 5, '{', '}');
        std::string denom = Between(eq, loc + 7 + numer.size(), '{', '}');

        eq.erase(loc, numer.size() + 7 + denom.size());
        eq.insert(loc, CmplxToStr(Evaluate(numer) / Evaluate(denom)));
    }

    // EXPONENTS
    loc = -1;
    while ((loc = eq.find('^', loc + 1)) != std::string::npos) {
        std::string exp = Between(eq, loc + 1, '{', '}');
        std::string base = FindCmplx(eq, loc, true);
        std::cout << "Found exponent with base " << base << " and exponent " << exp << std::endl;

        eq.erase(loc - base.size(), base.size() + 3 + exp.size());
        eq.insert(loc - base.size(), 
            CmplxToStr(std::pow(ParseComplex(base), Evaluate(exp))));
    }

    // OPERATORS ========================================================= OPERATORS
    std::cout << "Finding operators..." << std::endl;
    ubyte curOp = 0;
    size_t progress = 0;
    bool DNC = false;
    const char ops[] = { '/', '*', '-', '+' };
    while (DNC || isNan(ParseComplex(eq))) {
        if ((progress = eq.find(ops[curOp]), progress) == std::string::npos) {
            curOp++;
            progress = 0;
            DNC = true;
            continue;
        }
        DNC = false;

        std::string first = FindCmplx(eq, progress, true);
        std::string second = FindCmplx(eq, progress, false);
        std::cout << "Found operator " << ops[curOp] << " with first " << first << " and second " << second << std::endl;

        std::cout << "Old eq: " << eq;
        eq.erase(progress - first.size(), first.size() + 1 + second.size());
        std::cout << "; Replacing operation, new eq: '" << eq << '\'' << std::endl;

        std::string toReplace = CmplxToStr(operate(curOp, ParseComplex(first), ParseComplex(second)));
        std::cout << "Result of operation: " << CmplxToStr(operate(curOp, ParseComplex(first), ParseComplex(second))) << std::endl;

        eq.insert(progress - first.size(), toReplace);
        progress += (toReplace.size() - first.size()) + 1;
    }   

    return ParseComplex(eq);
} // End error scope (Not evaluate)

ERROR:
    std::cerr << "                                                    >>> COULD NOT EVALUATE EQ'" << eq << "' (" << reason << ")" << std::endl;
    return NaN;
} // End evaluate