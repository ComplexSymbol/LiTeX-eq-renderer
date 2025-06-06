#include <iostream>
#include <vector>
#include <string>
#include <complex>
#include <chrono>
#include <thread>
#include "Grapher.cpp"

int main() {
    std::string equation = "x!";

    for (ubyte anim = 0; anim < 127; anim++) {
        std::cout << "\x1B[2J\x1B[H" << std::flush;
        //system("clear");
        
        auto start = std::chrono::high_resolution_clock::now();
        Graph(equation, 0.0625, 0.0625, false, anim).Print();
        auto finish = std::chrono::high_resolution_clock::now();

        auto nanoseconds = std::chrono::duration_cast<std::chrono::nanoseconds>(finish-start);
        std::cout << "Graphed in " << nanoseconds.count() << "ns" << std::endl;

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    //cmplx eval = Evaluate(equation);
    //std::cout << eval << std::endl;

    return 0;
}
