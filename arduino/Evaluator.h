#ifndef _EVALUATOR_H
#define _EVALUATOR_H
#include <Arduino.h>
#include <LiTeX.h>

typedef unsigned char ubyte;
typedef signed char sbyte;
typedef std::complex<double> cmplx;

extern const cmplx NaN;

extern sbyte sgn(double val);
extern bool isNan(cmplx z);
extern double SafeStod(std::string str);

extern double roundD(double var, ubyte prec);

extern std::string CmplxToStr(cmplx z, ubyte prec = 6, bool forRender = false);

extern cmplx ParseComplex(std::string str);

extern std::string FindCmplx(std::string str, ubyte loc, bool before);

extern void AddImpMultTo(std::string &eq);

extern std::tuple<std::string, ubyte> FindMultiple(std::string &eq, std::vector<std::string> finds, std::vector<std::string> replace = {});

extern cmplx factorial(cmplx z);

extern void approximateFraction(double value, long long &p, long long &q, long long maxDenominator = 1000000);

extern cmplx nonPrincipalPow(cmplx cbase, cmplx cexponent);

extern cmplx Evaluate(std::string eq);

#endif