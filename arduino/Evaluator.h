#ifndef _EVALUATOR_H
#define _EVALUATOR_H
#include <Arduino.h>
#include <complex>
#include <string>
#include <vector>

typedef unsigned char ubyte;
typedef signed char sbyte;
typedef std::complex<long double> cmplx;

inline extern sbyte sgn(long double val);

extern std::string CmplxToStr(cmplx z, ubyte prec = 10, bool forRender = false);

extern cmplx ParseComplex(std::string str);

extern std::string FindCmplx(std::string str, ubyte loc, bool before);

extern void AddImpMultTo(std::string &eq);

extern std::tuple<std::string, ubyte> FindMultiple(std::string &eq, const std::vector<std::string> finds, std::vector<std::string> replace = {});

extern cmplx Evaluate(std::string eq);

#endif