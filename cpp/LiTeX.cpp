#include <iostream>
#include <string> 
#include <vector>
#include "renderFormat.cpp"

using namespace std;
void Testing() {
    Render a = Render(vector<unsigned long long>({0, 0b10100100, 0b01010010, 0x1f, 0, 0x1f}), 8);
    Render b = Render(vector<unsigned long long>({0x1f, 0, 0x1f, 0, 0xf1, 0}), 8);
    a.Print(true);
    b.Print(true);
    
    a = appendRenders(a, b, 0, 0, 2, 3);
    a.Print(true);
};