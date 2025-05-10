#include <iostream>
#include <vector>
#include <string>

#include <Evaluator.h>
#include <LiTeX.h>
#include <RenderEngine.h>
#include <DisplaySPI.h>

std::string equation = "1^{2}";

void setup() {
    setup_SPI();
    delay(2000);
    
    std::cout.flush();
    std::cout << "INIT INIT INIT" << std::endl;
}

void loop() { 
    std::cout << "LOOP LOOP LOOP" << std::endl;
    
    uint start = micros();
    Render renderEQ = GenerateRender(equation);
    uint finish = micros();
    renderEQ.Print(true);

    std::cout << "Generated render in: " << (finish - start) << "µs" << std::endl;

    start = micros();
    cmplx ans = Evaluate(equation);
    finish = micros();
    std::cout << "ANS: " << CmplxToStr(ans) << std::endl;
    
    std::cout << "Evaluated in: " << (finish - start) << "µs" << std::endl;

    std::cout << "Initializing display...\n" << std::endl;
    initialize_display();
    std::cout << "Software reset...\n" << std::endl;
    software_reset();
    std::cout << "Clearing display...\n" << std::endl;
    clear_display();

    std::cout << "Sending render..." << std::endl;
    send_render(renderEQ);
  
    delay(3000);
    std::cout << "EXITING..." << std::endl;
    kill_SPI();
    exit(0);
    return;
}
