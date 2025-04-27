#include <vector>
#include <iostream>
#include <bitset>
using namespace std;
typedef unsigned long long ull;

class Render {
    public:
    
    vector<ull> bitmap;
    int height;

    Render(vector<ull> bmap, int ht) {
        bitmap = bmap;
        height = ht;
    }

    void Print(bool prettyPrint=false) {
        cout << "DIMENSIONS: " << bitmap.size() << "x" << height << endl;
        for (int y = height - 1; y >= 0; y--) { // Print top to bottom
            for (int x = 0; x < bitmap.size(); x++) {
                if (prettyPrint) 
                    cout << (((bitmap[x] >> y) & 1) ? "██" : "  ");
                else 
                    cout << (((bitmap[x] >> y) & 1) ? "1" : "0");
            }
            cout << endl;
        }
    }
};

// Overlaps b over a at (x, y) and ORs all values.
// Original 'a' dimensions are returned. All values that do not overlap (hanging off) are ignored.
Render mergeRenders(Render a, Render b, int x, int y) {
    // Loop from x to min(x + b.bitmap.size, a.bitmap.size)

    // Why min? Because if x + b.bitmap.size > a.bitmap.size, 
    // then we get an index problem, this cuts off irrelevant b portions

    // Why not iterate from a to a.bitmap.size()? Because portions between 0 and x
    // aren't modified, so we don't have to loop over them.
    ull mask = (a.height >= 64) ? ~0ULL : ((1ULL << a.height) - 1); // careful if height == 64
    int stop = min(x + b.bitmap.size(), a.bitmap.size());

    for (int col = x; col < stop; col++) {
        a.bitmap[col] |= (b.bitmap[col - x] << y) & mask;
    }

    return a;
}

// Appends b to a. Aligns aAlign and bAlign y values so they are on the same level.
// Returns a larger bitmap.
// `a` gets appended with `b` and (aligns `a` and `b` OR overlaps `b` by `overlap` starting at height `overlapFrom`)
Render appendRenders(Render a, Render b, int aAlign = 0, int bAlign = 0, int overlap = 0, int overlapFrom = 0) {
    // Positive diff means b has to move up to match a
    // Negative diff means a has to move up to match b
    int diff = aAlign - bAlign;
    
    Render canvas = Render(
        vector<ull>(a.bitmap.size() + b.bitmap.size(), 0), // empty bitmap of a width + b width
        (overlap > 0) ? // Using overlap? 
        max(a.height, overlapFrom + b.height - overlap) : // Find the height when overlapping
        (a.height + max((aAlign - a.height) - (bAlign - b.height), 0) + max(bAlign - aAlign, 0)) // Find the height when aligned
    );

    // Place in bottom left corner, move up if diff requires
    canvas = mergeRenders(canvas, a, 0, 0/*diff < 0 ? -diff : 0*/);
    
    cout << "Canvas after one merge: \n";
    canvas.Print(true);

    // Place to the right of a, move up if diff requires OR if overlap requires
    canvas = mergeRenders(canvas, b, a.bitmap.size(), (overlap != 0) ? (overlapFrom - overlap) : (diff > 0 ? diff : 0));

    return canvas;
}

int max(int a, int b) {
    return a > b ? a : b;
}

int min(int a, int b) {
    return a < b ? a : b;
}