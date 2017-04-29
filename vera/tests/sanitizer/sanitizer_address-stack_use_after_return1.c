#include<stdio.h> 
#include<stdlib.h> 
char* func() 
{ 
	char c = 'a'; 
	return &c; 
} 
int main(int argc, char *argv[]) 
{ 
	char* ptr = func(); 
	char c = *ptr; 
	return 0; 
}