#include <stdlib.h>
#include <stdio.h>
int main(int argc, char** argv) 
{
	int res = -1;
	int* array = (int*)malloc(100*sizeof(int));
	array[ 0 ] = 0;
	if (array[ argc+ 100 ])// BOOM Heap-buffer-overflow
	{
		res = 1; 
	}
	free(array);
	return res;
}