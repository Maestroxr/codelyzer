#include<stdio.h> 
#include<stdlib.h> 
int main(void) 
{ 
	char* p = (char*)malloc(3); 
	if (!p)
	{
		printf("Memory error");
	}
	*p = 'a'; 
	*(p+1) = 'b'; 
	*(p+2) = 'c'; 
	free(p); 
	*p = 'a'; 
	return 0; 
}
