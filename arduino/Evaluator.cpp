#include <iostream>
#include <sstream>
#include <iomanip>
#include <cmath>
#include <complex>
#include <string>
#include <vector>
#include <map>
#include "LiTeX.cpp"

typedef std::complex<long double> cmplx;

const cmplx NaN(std::nan("0"), std::nan("0"));
inline bool isNan(cmplx z) { return z != z; }

inline sbyte sgn(long double val) {
    return (0 < val) - (val < 0);
}

std::string CmplxToStr(cmplx z, ubyte prec = 10, bool forRender = false) {
    return (z.imag() == 0 || z.real() == 0)
         ? (std::stringstream() << std::setprecision(prec) << (z.imag() == 0 ? z.real() : z.imag()) << (z.imag() == 0 ? "" : (forRender ? "\\im" : "i"))).str()
         : ("(" + (std::stringstream() << std::setprecision(prec) << z.real()).str() + (sgn(z.imag()) >= 0 ? "+" : "") + (std::stringstream() << z.imag()).str() + "i)");
}

// PARSE COMPLEX ===================================================================== PARSE COMPLEX
cmplx ParseComplex(std::string str) {
    if (str == "(nan+nani)") return NaN;

    long double real = 0;
    long double imag = 0;
    bool opFound = false;
    ubyte start = 0;
    std::string reason = "";

PARSE_START:
    ubyte stop = str.size() - (str[str.size() - 1] == ')' ? 1 : 0);
    start += (str[0] == '(' && start == 0 ? 1 : 0);
    for (ubyte i = start; i < stop; i++) {
        if (i == start && str[i] == '-') continue;
        
        bool isEnd = i == stop - 1;

        if (str[i] == '-' || str[i] == '+') {
            if (str[i - 1] == 'e')
                continue; // It's fine guys. Don't worry about the exponent
            
            opFound = true;
            
            if (str[i - (isEnd ? 0 : 1)] == 'i') {
                if (imag != 0) {
                    reason = "Multiple imaginary parts found";
                    goto ERROR; // Woah, we already found imag part
                }
                
                std::string strImag = str.substr(start, i - start + (isEnd ? 0 : -1));
                if (strImag.empty()) strImag = "1"; // Otherwise (1+i) => Error
                imag = std::stold(strImag);
                
                break; // Let's get out of here
            }
            else {
                if (real != 0) {
                    reason = "Multiple real parts found";
                    goto ERROR; // Woah, we already found real part
                }

                real = std::stold(str.substr(start, i - start + (isEnd ? 1 : 0)));
                start = i + (str[i] == '+' ? 1 : 0);
                
                if (!isEnd)
                    goto PARSE_START; // Restart parsing cuz there still might be imag part
                break;
            }
        }

        if (!(isdigit(str[i]) || str[i] == 'e' || str[i] == '.' || str[i] == 'i')) {
            reason = "Unrecongized character " + std::string(1, str[i]);
            goto ERROR;
        }

        else if (str[i] == 'i') {
            if (i != stop - 1) {
                reason = "Imaginary portion may only appear at end of string";
                goto ERROR;
            }
            std::string coeff = str.substr(start, i - start);
            imag = std::stold(coeff != "" ? (coeff != "-" ? coeff : "-1") : "1");
        }

        else if (isEnd) {
            // Because other parts would catch an imaginary number, the number must be real
            // Or, in the erroneous format a+a
            if (opFound || str[0] == '(') {
                reason = "Invalid format";
            goto ERROR;
            }
            return cmplx(std::stold(str));
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
// Returns complex-parseable string.
std::string FindCmplx(std::string str, ubyte loc, bool before) {
    ubyte minusCount = 0;
    ubyte plusCount = 0;
    bool isEnd = false;
    std::string reason = "";

    for (ubyte i = loc + (before ? -1 : 1); 
        before ? (i >= 0) : (i < str.size()); 
        i += (before ? -1 : 1)
    ) {
        isEnd = i == (before ? 0 : str.size() - 1);

        if (i == loc - 1 && before && str[i] == ')') {
            return "(" + Between(str, i, ')', '(', true) + ")";
        }
        else if (i == loc + 1 && !before && str[i] == '(')
            return "(" + Between(str, i, '(', ')') + ")";

        if (str[i] == '+') {    // Must be part of exp 
            if (str[i - 1] != 'e' || plusCount > 0) {
                return before 
                    ? str.substr(i + 1, loc - i - 1)
                    : str.substr(loc + 1, i - loc - 1); 
            }
            plusCount++;
        }
        
        else if (str[i] == '-') { // Found minus, could be negative or e-...
            if (!before) {
                if (i == loc + 1) {
                    minusCount++;
                }
                else if (str[i - 1] != 'e' || minusCount > 1)
                    return str.substr(loc + 1, i - loc - 1);
            }
            else {
                if (str[i - 1] != 'e') {
                    return str.substr(i + 1, loc - i - 1);
                }
            }
        }
        else if (str[i] == 'i' && !before)
            return str.substr(loc + 1, i - loc);

        // Encountered unidentified character, must be end of number
        else if (!(isdigit(str[i]) || str[i] == 'e' || str[i] == '.' || (str[i] == 'i' && before && i == loc - 1))) {
            return before ? str.substr(i + 1, loc - i - 1) : str.substr(loc + 1, i - loc - 1);
        }
        else if (isEnd)
            return before ? str.substr(i, loc - i) : str.substr(loc + 1, i - loc);
    }

ERROR:
    std::cerr << "                                                    >>> COULD NOT FIND COMPLEX IN STR " << str << " (loc: " << (int)loc << ") Reason: " << reason << std::endl;
    return "";
}

// ADD IMP MULT ====================================================================== ADD IMP MULT
void AddImpMultTo(std::string& eq) {
    for (ubyte i = 0; i < eq.size() - 1; i++) {
        if ((isdigit(eq[i]) && eq[i + 1] == '\\' && eq[i + 2] != 'i') || // 5\pi but not 5\im
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
        if (eq.size() > 0xFF) goto ERROR;
    }
    return;
ERROR:
    std::cerr << "EQUATION BECAME TOO LARGE WHILE ADDING IMPLICIT MULTIPLICATION IN EQ: " << eq << std::endl;
    std::terminate();
}

// TRIG MAPS AND OPS ================================================================= TRIG MAPS AND OPS
const std::unordered_map<std::string, ubyte> trigMap = {
    { "sin", 1 },
    { "cos", 2 },
    { "tan", 3 },
    { "sec", 4 },
    { "csc", 5 },
    { "cot", 6 },
    { "sinh", 7 },
    { "cosh", 8 },
    { "tanh", 9 },
    { "sin^{-1}", 10 },
    { "cos^{-1}", 11 },
    { "tan^{-1}", 12 },
};
auto operateTrig = [](std::string func, cmplx n) {
    switch (trigMap.at(func)) {
        case 1: return sin(n);
        case 2: return cos(n);
        case 3: return tan(n);
        case 4: return cmplx(1,0) / sin(n);
        case 5: return cmplx(1,0) / cos(n);
        case 6: return cmplx(1,0) / tan(n);
        case 7: return cosh(n);
        case 8: return cosh(n);
        case 9: return cosh(n);
        case 10: return asin(n);
        case 11: return acos(n);
        case 12: return atan(n);
    }
    return NaN;
};

// REGULAR OPS
auto operate = [](ubyte op, cmplx a, cmplx b) {
    switch (op) {
        case 0: return a / b;
        case 1: return a * b;
        case 2: return a - b;
        case 3: return a + b;
    }
    return NaN;
};

// MULTI FIND ======================================================================== MULTI FIND
std::tuple<std::string, ubyte> FindMultiple(std::string &eq, std::vector<std::string> finds, std::vector<std::string> replace = {}) {
    bool noReplace = replace == std::vector<std::string>({});
    for (ubyte i = 0; i < size(eq); i++) {
        for (ubyte n = 0; n < finds.size(); n++) {
            if (eq.substr(i, finds[n].size()) == finds[n]) { // Found find
                if (noReplace) // Just return the index
                    return std::tuple<std::string, ubyte>(finds[n], i);
                else {
                    // Replace find with replace[n]
                    eq.erase(i, finds[n].size());
                    eq.insert(i, replace[n]);
                    if (eq.size() > 0xFF) goto ERROR;
                }
            }
        }
    }

    if (!noReplace)
        std::cerr << "                                                    >>> COULD NOT FIND MULTIPLES IN EQ: '" << eq << "'" << std::endl;
    return std::tuple<std::string, ubyte>("", 0xFF);

ERROR:
    std::cerr << "EQUATION BECAME TOO LARGE WHILE REPLACING MULTIPLES IN EQ: '" << eq << "'" << std::endl;
    std::terminate();
}

// ADDITIONAL MATH FUNCS ============================================================= ADDITIONAL MATH FUNCS
cmplx factorial(cmplx z) {
    return z.imag() == 0 && z.real() >= 0
        ? cmplx(std::tgammal(z.real() + 1), 0)
        : std::sqrt(cmplx(2*M_PI, 0) / (z += 1)) * std::pow((z / cmplx(M_E, 0)) * std::sqrt(z * cmplx(0, -1) * std::sin(cmplx(0, 1) / z)), z);
}

// EVALUATE ========================================================================== EVALUATE
cmplx Evaluate(std::string eq) {
    std::cout << "Evaluating eq " << eq << " (len: " << eq.size() << ")" << std::endl;
    std::string reason = "";
{ // Scope so that 'goto ERROR' will not bypass variable initialization
    if (eq.size() >= 0xFF) {
        reason = "That's a really big and chonky equation you got there. I can't evaluate that.";
        goto ERROR;
    }

    // SETUP EQUATION
    {   cmplx test; // Is eq a number? (Scope so test is del)
        std::cout << "Testing whether eq is complex..." << std::endl;
        if (!isNan(test = ParseComplex(eq))) return test;   }

    AddImpMultTo(eq);
    
    // ` is placeholder character for renderer.
    if (eq.find('`') != std::string::npos) { reason = "Equation has placeholders"; goto ERROR; }

    {
        // REPLACE CONSTANTS
        std::tuple<std::string, ubyte> loc;
        while ((loc = FindMultiple(eq, 
            std::vector<std::string>({ "\\e", "\\pi", "\\im" }),
            std::vector<std::string>({ "2.718281828459045", "3.141592653589793", "i" }))) 
            != std::tuple<std::string, ubyte>("", 0xFF)) {}

        // TRIGONOMETRIC FUNCTIONS
        std::cout << "Finding trig functions..." << std::endl;
        while((loc = FindMultiple(eq, std::vector<std::string>({ "sin", "cos", "tan", "sec", "csc", "cot", "sinh", "cosh", "tanh", "sin^{-1}", "cos^{-1}", "tan^{-1}" }))) != std::tuple<std::string, ubyte>("", 0xFF)) {
            std::cout << "Found trig function " << std::get<0>(loc) << std::endl;
            std::string contents = Between(eq, std::get<1>(loc) + std::get<0>(loc).size(), '(', ')');
            
            eq.erase(std::get<1>(loc), std::get<0>(loc).size() + contents.size() + 2);
            eq.insert(std::get<1>(loc), CmplxToStr(operateTrig(std::get<0>(loc), Evaluate(contents))));
        }
    }

    AddImpMultTo(eq);
    std::cout << "Evaluating standardized equation " << eq << std::endl;

    // LOGARITHMS
    size_t loc = -1;
    while((loc = eq.find("log", loc + 1)) != std::string::npos) {
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
        bool beforeExp = eq[contents.size() + 2] == '^';

        cmplx toRepl = ParseComplex("(" + contents + ")");
        if (isNan(toRepl)) toRepl = Evaluate(contents);

        eq.erase(loc, contents.size() + 2);
        eq.insert(loc, beforeExp ? "(" + CmplxToStr(toRepl) + ")" : CmplxToStr(toRepl));
    }
    std::cout << "EQ after paren: " << eq << std::endl;
    
    // RADICALS
    loc = -1;
    while ((loc = eq.find("\\sqrt", loc + 1)) != std::string::npos) {
        std::string nth = Between(eq, loc + 5, '{', '}');
        std::string root = Between(eq, loc + 7 + nth.size(), '{', '}');

        eq.erase(loc, nth.size() + 9 + root.size());
        eq.insert(loc, CmplxToStr(pow(Evaluate(root), cmplx(1, 0) / Evaluate(nth))));
    }

    // FRACTIONS
    loc = -1;
    while ((loc = eq.find("\\frac", loc + 1)) != std::string::npos) {
        std::string numer = Between(eq, loc + 5, '{', '}');
        std::string denom = Between(eq, loc + 7 + numer.size(), '{', '}');

        eq.erase(loc, numer.size() + 9 + denom.size());
        eq.insert(loc, CmplxToStr(Evaluate(numer) / Evaluate(denom)));
    }

    // EXPONENTS
    loc = -1;
    while ((loc = eq.find('^', loc + 1)) != std::string::npos) {
        bool isParen = eq[loc - 1] == ')';

        std::string exp = Between(eq, loc + 1, '{', '}');
        std::string base = isParen ? Between(eq, loc - 1, ')', '(', true) : FindCmplx(eq, loc, true);
        std::cout << "(isparen: " << isParen << ") Found exponent with base " << base << " and exponent " << exp << std::endl;

        eq.erase(loc - base.size() - (isParen ? 2 : 0), base.size() + (isParen ? 5 : 3) + exp.size());
        eq.insert(loc - base.size()- (isParen ? 2 : 0), 
            CmplxToStr(std::pow(ParseComplex(base), Evaluate(exp))));
    }

    loc = -1;
    while ((loc = eq.find('!', loc + 1)) != std::string::npos) {
        std::string num = FindCmplx(eq, loc, true);

        if (eq[0] == '-' && num.size() + 1 == loc)
            num = '-' + num;

        std::cout << "Found factorial with number " << ParseComplex(num) << std::endl;
        if (ParseComplex(num).real() < 0) {
            reason = "Factorial only supported for Re(z) >= 0";
            goto ERROR;
        }
        
        eq.erase(loc - num.size(), num.size() + 1);
        eq.insert(loc - num.size(), CmplxToStr(factorial(ParseComplex(num))));
    }

    loc = -1;
    std::tuple<std::string, ubyte> locFunc;
    while ((locFunc = FindMultiple(eq, std::vector<std::string>({"\\perm", "\\comb"}))) != std::tuple<std::string, ubyte>("", 0xFF)) {
        // Implicit multiplication will make it ...*\perm*...
        std::string n = FindCmplx(eq, std::get<1>(locFunc) - 1, true);
        std::string r = FindCmplx(eq, std::get<1>(locFunc) + 5, false);

        if (eq[0] == '-' && n.size() + 1 == std::get<1>(locFunc))
            n = '-' + n;

        cmplx Nparsed = ParseComplex(n);
        cmplx Rparsed = ParseComplex(r);
        
        cmplx permute = factorial(Nparsed) / (factorial(Nparsed - Rparsed));
        std::cout << "Found " << std::get<0>(locFunc) << " with n:" << n << " and r:" << r << " permute:" << permute << std::endl;
        
        eq.erase(std::get<1>(locFunc) - n.size() - 1, n.size() + 7 + r.size());
        eq.insert(std::get<1>(locFunc) - n.size() - 1,
            CmplxToStr(
                std::get<0>(locFunc) == "\\perm" 
                ? permute
                : permute / factorial(Rparsed)
            )
        );
    }

    if (eq.find("nan") != std::string::npos) {
        reason = "NaN in eq";
        goto ERROR;
    }

    // OPERATORS ========================================================= OPERATORS
    std::cout << "Finding operators..." << std::endl;
    ubyte curOp = 0;
    size_t progress = 1;
    bool DNC = false;
    const char ops[] = { '/', '*', '-', '+' };
    while (DNC || isNan(ParseComplex(eq))) {
        if ((progress = eq.find(ops[curOp], progress)) == std::string::npos) {
            std::cout << "Could not find operator " << ops[curOp] << " in eq: " << eq << std::endl;
            curOp++;
            progress = 1;
            DNC = true;
            continue;
        }
        DNC = false;

        if ((curOp == 2 || curOp == 3) && eq[progress - 1] == 'e') {
            std::cout << "Skipping exponent operator" << std::endl;
            progress++;
            continue;
        }

        std::string first = FindCmplx(eq, progress, true);
        std::string second = FindCmplx(eq, progress, false);

        std::cout << "Progress: " << progress << " Found operator " << ops[curOp] << " with first " << ParseComplex(first) << " and second " << ParseComplex(second) << std::endl;
        std::cout << "Result of operation: " << CmplxToStr(operate(curOp, ParseComplex(first), ParseComplex(second))) << std::endl;

        if (first.empty()) {
            std::cout << "First is empty!" << std::endl;
            progress++;
            continue;
        }
        
        if (eq[progress - first.size() - 1] == '(' &&
            eq[progress + second.size() + 1] == ')'
        ) {
            std::cout << "Operation is already a number" << std::endl;
            progress++;
            continue;
        }

        if (eq[0] == '-' && first.size() + 1 == progress)
            first = '-' + first;

        std::cout << "Old eq: " << eq << std::endl;
        eq.erase(progress - first.size(), first.size() + 1 + second.size());

        std::string toReplace = CmplxToStr(operate(curOp, ParseComplex(first), ParseComplex(second)));
        eq.insert(progress - first.size(), toReplace);
        std::cout << "new eq: '" << eq << '\'' << std::endl;

        progress += (toReplace.size() - first.size());
        std::cout << "new progress: " << progress << std::endl;
    }   

    std::cout << "Finished evaluating... ans: " << eq << std::endl;
    return ParseComplex(eq);
} // End error scope (Not evaluate)

ERROR:
    std::cerr << "                                                    >>> COULD NOT EVALUATE EQ'" << eq << "' (" << reason << ")" << std::endl;
    return NaN;
} // End evaluate