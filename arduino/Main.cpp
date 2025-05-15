#include <iostream>
#include <vector>
#include <string>
#include <complex>
#include <chrono>
#include "Evaluator.cpp"

int main() {
    std::string equation = "";

    //auto start = std::chrono::high_resolution_clock::now();
    //Render renderEQ = GenerateRender(equation);
    //auto finish = std::chrono::high_resolution_clock::now();

    //auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(finish-start);
    //std::cout << "Rendered in " << nanoseconds.count() << "ns\n" << std::endl;

    auto start = std::chrono::high_resolution_clock::now();
    cmplx ans = Evaluate(equation);
    auto finish = std::chrono::high_resolution_clock::now();

    auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(finish-start);
    std::cout << "Evaluated in " << nanoseconds.count() << "ns\n" << std::endl;
    std::cout << CmplxToStr(ans) << std::endl;
    
    //Render renderANS = GenerateRender("=" + CmplxToStr(ans, 4, true));
    
    //renderEQ.Print(true);
    // renderANS.Print(true);

    return 0;
}
