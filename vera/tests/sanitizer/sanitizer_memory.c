#include <stdlib.h>
#include <stdio.h>
int main(int argc, char** argv) 
{
	int res = -1;
	int* arr = (int*)malloc(7*sizeof(int));
	arr[ 2 ] = 0;  //  - OK - Write to uninitialized memory
	if (arr[ 3 ]) // BOOM  - Read from uninitialized memory
	{
		res = 1;
	}
	free(arr);
	return res;
}