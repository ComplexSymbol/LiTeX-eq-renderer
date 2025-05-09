#include <iostream>
#include <vector>
#include <string>
#include <complex>
#include <chrono>
#include "Evaluator.cpp"

int main() {
    std::string equation = "\\sqrt{2}{2}";
    
    auto start = std::chrono::high_resolution_clock::now();
    cmplx ans = Evaluate(equation);
    auto finish = std::chrono::high_resolution_clock::now();

    auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(finish-start);
    std::cout << "Evaluated in " << nanoseconds.count() << "ns\n";

    std::cout << CmplxToStr(ans) << std::endl;

    return 0;
}
