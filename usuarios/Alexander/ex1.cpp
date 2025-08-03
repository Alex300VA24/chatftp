#include <iostream>
#include <vector>

using namespace std;

int main() {
    vector<int> c = {4, 6, 2, 7};

    c.push_back(5);
    c.push_back(1);
    c.push_back(9);

    for (int i = 0; i < c.size(); i++) {
        cout << c[i] << " ";
    }
    cout << endl;

    c.pop_back();
    c.pop_back();

    for (long unsigned int i = 0; i < c.size(); i++) {
        cout << c[i] << " ";
    }
    cout << endl;

    cout << c.front() << " " << c.back() << endl;

    return 0;
}