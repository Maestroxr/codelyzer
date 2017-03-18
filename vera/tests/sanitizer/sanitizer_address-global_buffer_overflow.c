#include <stdlib.h>
#include <stdio.h>
int globalArray[ 100 ] = {-1 };
int main(int argc, char** argv) 
{
	int res = -1;
	/*
		Address Sanitizer
	*/
	
	
	if (globalArray[ argc+ 100 ])
	{
		// BOOM Global-buffer-overflow
		res = globalArray[ argc + 100 ];  // BOOM Global-buffer-overflow
	}
	
	/***/
	return res;
}