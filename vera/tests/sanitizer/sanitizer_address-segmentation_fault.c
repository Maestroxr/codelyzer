/* SEGMENTATION FAULT */
#include<stdio.h> 
#include<stdlib.h> 
#include<string.h> 

int main(void) 
{ 
	char* p; 

	p[ 100 ] = 'a';
	printf("\n %s \n", p); 

	return 0; 
}