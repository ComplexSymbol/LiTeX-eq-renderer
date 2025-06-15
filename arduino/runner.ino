#include <iostream>
#include <vector>
#include <string>
#include <iomanip>

#include <Grapher.h>

std::string equation = "3\\sqrt{2}{\\frac{sin(4)}{3}}";

void setup() {
  //setup_SPI();
  delay(2000);

  std::cout.precision();
  Serial.begin(9600);

  Serial.println("SERIAL: INIT");
  delay(100);
}

void loop() {
  Serial.println("SERIAL: LOOP");
  delay(100);
  
  uint start = micros();
  cmplx eval = Evaluate(equation);
  uint finish = micros();

  SerialPrintlnString("Finished Evaluating! Result:");
  SerialPrintlnString(CmplxToStr(eval));

  SerialPrintlnString("Evaluated equation in: " + std::to_string(finish - start) + "µs");

  //std::cout << "Initializing display...\n" << std::endl;
  //initialize_display();
  //std::cout << "Software reset...\n" << std::endl;
  //software_reset();
  //std::cout << "Clearing display...\n" << std::endl;
  //clear_display();

  //std::cout << "Sending render..." << std::endl;
  //send_render(graph);

  delay(3000);
  SerialPrintlnString("EXITING...");
  //kill_SPI();
  exit(0);
  return;
}
