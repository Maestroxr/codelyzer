#include <stdlib.h>
#include <stdio.h>
int main(int argc, char** argv) 
{
	int* arr = (int*)malloc(7*sizeof(int));
	arr[ 2 ] = 0;  //  - OK - Write to uninitialized memory
	if (arr[ argc ]) // BOOM  - Read from uninitialized memory
	{
		printf("xx\n");
	}
	free(arr);
	return 0;
}