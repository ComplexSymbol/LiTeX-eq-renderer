#include <Evaluator.h>
#include <iostream>
#include <cmath>
#include <complex>
#include <string>

typedef unsigned char ubyte;
typedef signed char sbyte;

std::complex<double> ParseComplex(std::string str) {
    double real = 0;
    double imag = 0;
    ubyte start = 0;

PARSE_START:
    sbyte negate = 1;

    for (ubyte i = start; i < str.size(); i++) {
        if (i == start && str[i] == '-') {
            negate = -1;
            continue;
        }
        
        // We found the end of a number! (Or the string ended (or it's just part of sci notation))
        if (str[i] == '-' || str[i] == '+' || i == str.size() - 1) {
            if (str[i - 1] == 'e')
                continue; // It's fine guys. Don't worry about the exponent
            
            if (str[i - 1] == 'i') {
                if (imag != 0) goto ERROR; // Woah, we already found imag part

                imag = std::stod(str.substr(start, i - start - 1)) * negate;
                break; // Let's get out of here
            }
            else {
                if (real != 0) goto ERROR;

                real = std::stod(str.substr(start, i - start)) * negate;
                start = i;
                goto PARSE_START; // Restart parsing cuz there still might be imag part
            }
        }

        if (!(isdigit(str[i]) || str[i] == 'e'))
            goto ERROR;
    }

    std::cout << "Successfully parsed '" << str << " as (" << real << ", " << imag << ")." << std::endl;
    return std::complex<double>(real, imag);

ERROR:
    std::cerr << "COULD NOT PARSE " << str << std::endl;
}