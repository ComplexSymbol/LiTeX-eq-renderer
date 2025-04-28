#include <iostream>
#include <string> 
#include <vector>
#include "renderFormat.cpp"

using namespace std;
Render GenerateRender(string eq, bool exp = false) {
    for (char c : eq) {

    }
}

void Test() {
    Render r = Render(vector<ull>({ 0, 65, 129, 511, 1, 1 }), 10);
    r.Print(true);
}