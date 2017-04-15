/* SEGMENTATION FAULT */
#include<stdio.h> 
#include<stdlib.h> 
#include<string.h> 

int main(void) 
{ 
	char* p; 

	strcat(p, "abc"); 
	printf("\n %s \n", p); 

	return 0; 
}