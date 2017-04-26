#include<stdio.h> 
#include<stdlib.h> 
int main(void) 
{ 
	char* p; 
	p[ 1000 ] = 'a';
	printf("\n %s \n", p); 
	return 0; 
}