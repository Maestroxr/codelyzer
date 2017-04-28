#include<stdio.h> 
#include<stdlib.h> 
int main(void) 
{ 
	int result = 0;
	char* p = (char*)malloc(3); 
	if (!p) 
	{
		result = -1;
	}
	int i = 0; 
	for(i=0;i<0Xffffffff;i++) 
	{ 
		p[ i ] = 'a'; 
	} 
	printf("\n %s \n", p); 
	return result; 
}