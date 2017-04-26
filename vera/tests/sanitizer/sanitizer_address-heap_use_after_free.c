#include <stdlib.h>
#include <stdio.h>

int main(int argc, char** argv) 
{
	int res = -1;
	int* array = (int*)malloc(100*sizeof(int));
	free(array);
	if (array[ argc ])// BOOM Heap-use-after-free	
	{
		res = 1;
	}
	return res;
}