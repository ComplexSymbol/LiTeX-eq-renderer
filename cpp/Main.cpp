#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include "LiTeX.cpp"

int main()
{
    std::string equation = "\\sqrt{\\frac{1}{2}}{1}+\\frac{1}{2}";

    auto start = std::chrono::high_resolution_clock::now();
    Render renderEQ = GenerateRender(equation);
    auto finish = std::chrono::high_resolution_clock::now();

    renderEQ.Print(true);

    auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(finish-start);
    std::cout << "Generated render in: " << nanoseconds.count() << "ns\n";
    return 0;
}
