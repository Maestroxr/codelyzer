#include <stdlib.h>
#include <stdio.h>
int globalArray[ 100 ] = {-1 };
int main(int argc, char** argv) 
{
	int res = -1;
	if (globalArray[ argc+ 100 ]) // BOOM Global-buffer-overflow
	{
		res = 1; 
	}
	return res;
}