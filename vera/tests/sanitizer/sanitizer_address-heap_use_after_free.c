#include <stdlib.h>
#include <stdio.h>

int main(int argc, char** argv) 
{
	int res = -1;
	
	/*
		Address Sanitizer
	*/
	
	int* array = new int[ 100 ];
	delete [] array;
	if (array[ argc ])
	{
		// BOOM Heap-use-after-free		-V-
		res = array[ argc ];  // BOOM Heap-use-after-free
	}
	
	/***/
	return res;
}