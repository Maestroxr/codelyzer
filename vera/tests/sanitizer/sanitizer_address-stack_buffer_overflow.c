#include <stdlib.h>
#include <stdio.h>

int main(int argc, char** argv) 
{
	int res = -1;
	int stackArray[ 100 ] = { 0 };
	if (stackArray[ argc+ 100 ])
	{
		// BOOM Stack-buffer-overflow
		res = stackArray[ argc + 100 ];  // BOOM Stack-buffer-overflow
	}
	return res;
}