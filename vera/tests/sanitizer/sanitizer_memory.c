#include <stdlib.h>
#include <stdio.h>

int main(int argc, char** argv) 
{
	int res = -1;
	/*
		Memory Sanitizer
	*/
	int* arr = (int*)malloc(7*sizeof(int));
	arr[ 2 ] = 0; // BOOM Uninitialized memory read   -V-
	if (arr[ 3 ]) 
	{
		printf("xx\n");
	}
	
	if (!arr)
	{
		res = -2;
	}
	free(arr);
	return res;
}