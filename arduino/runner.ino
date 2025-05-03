#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <LiTeX.h>
#include <RenderEngine.h>

std::string equation = "2^{2}^{2}";

void setup() {
}

void loop() {
    auto start = std::chrono::high_resolution_clock::now();
    Render renderEQ = GenerateRender(equation);
    auto finish = std::chrono::high_resolution_clock::now();

    renderEQ.Print(true);

    auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(finish-start);
    std::cout << "Generated render in: " << nanoseconds.count() << "ns\n";
    return;
}
