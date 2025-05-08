#include <iostream>
#include <cmath>
#include <complex>
#include <string>
#include <vector>
#include "LiTeX.cpp"

typedef unsigned char ubyte;
typedef signed char sbyte;
typedef std::complex<double> cmplx;

const cmplx NaN(std::nan("0"), std::nan("0"));
inline bool isNan(cmplx z) { return z != z; }

sbyte sgn(double val) {
    return (0 < val) - (val < 0);
}

inline std::string CmplxToStr(cmplx z) {
    return (z.imag() == 0 || z.real() == 0)
         ? (std::stringstream() << (z.imag() == 0 ? z.real() : z.imag()) << (z.imag() == 0 ? "" : "i")).str()
         : ("(" + (std::stringstream() << z.real()).str() + (sgn(z.imag()) >= 0 ? "+" : "") + (std::stringstream() << z.imag()).str() + "i)");
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

auto operate = [](ubyte op, cmplx a, cmplx b) {
    switch (op) {
        case 0:
            return a / b;
        case 1:
            return a * b;
        case 2:
            return a - b;
        case 3:
            return a + b;
    }
    return NaN;
};

// EVALUATE ========================================================================== EVALUATE
cmplx Evaluate(std::string eq) {
    std::string reason = "";
{ // Scope so goto ERROR will not bypass variable initialization
    
    // SETUP EQUATION ==================================================== SETUP EQUATION
    {   cmplx test; // Is eq a number? (Scope so test is del)
        if (!isNan(test = ParseComplex(eq))) return test;   }

    AddImpMultTo(eq);
    
    // ` is placeholder character for renderer.
    if (eq.find('`') != std::string::npos) { reason = "Equation has placeholders"; goto ERROR; }

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