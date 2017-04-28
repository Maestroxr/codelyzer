#include<stdio.h> 
#include<stdlib.h> 
int main(int argc, char *argv[]) 
{ 
	char* p = (char*)malloc(8); 
	if (!p) 
	{
		printf("malloc error");
	}
	free(p); 
	free(p); 
	return 0; 
}