#include <iostream>
#include <vector>
#include <string>

#include <LiTeX.h>
#include <RenderEngine.h>
#include <DisplaySPI.h>

std::string equation = "1 + \\e^{2\\pi\\im} - 3\\sqrt{2}{\\frac{sin(4)}{3}}";

void setup() {    
    delay(3000);
    
    std::cout.flush();
    std::cout << "INIT INIT INIT" << std::endl;  
}

void loop() {
    std::cout << "LOOP LOOP LOOP" << std::endl;
    
    uint start = micros();
    Render renderEQ = GenerateRender(equation);
    uint finish = micros();

    renderEQ.Print(true);

    std::cout << "Generated render in: " << (finish - start) << "µs\n";

    delay(1000);
    std::cout << "EXITING..." << std::endl;
    exit(0);
    return;
}
