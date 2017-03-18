#include <stdlib.h>
#include <stdio.h>

int main(int argc, char** argv) 
{
	int res = -1;
	/*
		Address Sanitizer
	*/
	
	int* array = new int[ 100 ];
	array[ 0 ] = 0;
	if (array[ argc+ 100 ])
	{
		// BOOM Heap-buffer-overflow	-V-
		res = array[ argc + 100 ];  // BOOM Heap-buffer-overflow
	}
	delete [] array;
	
	/***/
	return res;
}