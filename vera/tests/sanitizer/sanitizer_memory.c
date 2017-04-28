#include <stdlib.h>
#include <stdio.h>
int main(int argc, char** argv) 
{
	int* arr = (int*)malloc(7*sizeof(int)), result = 0;
	if (!arr) 
	{
		result = -1;
	}
	arr[ 2 ] = 0;  //  - OK - Write to uninitialized memory
	if (arr[ argc ]) // BOOM  - Read from uninitialized memory
	{
		printf("Read from uninitialized memory");
	}
	free(arr);
	return result;
}