#include <stdlib.h>
#include <stdio.h>

int main(int argc, char** argv) 
{
	int res = -1;
	/*
		Memory Sanitizer
	*/
	int* arr = new int[ 10 ];
	arr[ 5 ] = 0; // BOOM Uninitialized memory read   -V-
	if (arr[ 7 ]) 
	{
		printf("xx\n");
	}

	
	return res;
}