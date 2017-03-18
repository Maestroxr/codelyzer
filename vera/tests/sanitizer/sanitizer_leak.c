#include <stdlib.h>
#include <stdio.h>
int main(int argc, char** argv) 
{
	int res = -1;
	/*
		Leak Sanitizer
	*/
	void* p = (void*)malloc(7);
	if (!p)
	{
		//do something one
	}
	p = 0; // The memory is leaked here.	-V-
	p = (void*)malloc(7);
	if (!p)
	{
		//do something one
	}
	p = 0; // The memory is leaked here.	-V-
	/***/
	
	return res;
}