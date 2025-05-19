#include <iostream>
#include <vector>
#include <string>
#include <iomanip>

#include <Evaluator.h>
#include <LiTeX.h>
#include <RenderEngine.h>
#include <DisplaySPI.h>
#include <Grapher.h>

std::string equation = "x";

void setup() {
    setup_SPI();
    delay(2000);
    
    std::cout.flush();
    std::cout.precision();
    std::cout << "INIT INIT INIT" << std::endl;
}

void loop() { 
    std::cout << "LOOP LOOP LOOP" << std::endl;
    
    uint start = micros();
    Render graph = Graph(equation);
    uint finish = micros();
    graph.Print();

    std::cout << "Generated graph in: " << (finish - start) << "µs" << std::endl;

    std::cout << "Initializing display...\n" << std::endl;
    initialize_display();
    std::cout << "Software reset...\n" << std::endl;
    software_reset();
    std::cout << "Clearing display...\n" << std::endl;
    clear_display();

    std::cout << "Sending render..." << std::endl;
    send_render(graph);
  
    delay(3000);
    std::cout << "EXITING..." << std::endl;
    kill_SPI();
    exit(0);
    return;
}
