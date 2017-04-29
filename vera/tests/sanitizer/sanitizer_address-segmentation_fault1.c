#include<stdio.h> 
#include<stdlib.h> 
#include<string.h> 
void func(char ** argv) 
{ 
	char arr[ 2 ] = { 0 }; 
	strcpy(arr, argv[ 1 ]); 
	return; 
} 
int main(int argc, char *argv[]) 
{ 
	func(argv); 
	return 0; 
}