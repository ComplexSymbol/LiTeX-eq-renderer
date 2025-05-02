#include <iostream>
#include <vector>
#include <string>
#include "LiTeX.cpp"

int main()
{
    std::string equation = "2^{3^{2}}";
    Render renderEQ = GenerateRender(equation);
    renderEQ.Print(true);

    return 0;
}
