#include <iostream>
#include <string>
using namespace std;

int main() {

	// Asignación válida
	int x = 5;
	double y = 2.0;
	std::string z = "Hello";
	x=x+y;
	// Error de coincidencia de tipos
	y=y+x;
	// Error de variable indefinida
	cout << z << endl;
	return 0;
}