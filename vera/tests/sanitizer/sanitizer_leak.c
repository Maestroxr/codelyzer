#include <stdlib.h>
#include <stdio.h>
int main(int argc, char** argv) 
{
	int res = -1;
	void* p = (void*)malloc(7);
	if (!p)
	{
		res = 1;
	}
	p = (void*)malloc(7); // The memory is leaked here - no use of free()
	if (!p)
	{
		res = 2;
	}
	return res; // The memory is leaked here - no use of free()
}