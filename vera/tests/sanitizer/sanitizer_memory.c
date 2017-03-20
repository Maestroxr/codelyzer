#include <stdlib.h>
#include <stdio.h>

int main(int argc, char** argv) 
{
	int res = -1;
	/*
		Memory Sanitizer
	*/
	int* arr = (int*)malloc(7);
	arr[ 5 ] = 0; // BOOM Uninitialized memory read   -V-
	if (arr[ 7 ]) 
	{
		printf("xx\n");
	}

	if (!arr)
	{
		res = -2;
	}
	return res;
}