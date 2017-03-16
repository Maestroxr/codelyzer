#include <iostream>
#define BLA "blo"


#define CONST_INT 2
int main() 
{
	const int CONSTANT_INT = 2;
	int x = 5, i = 2; 
	char c= 'c';
	int arr[ CONST_INT ] = { 0 };
	char name[ CONST_INT ] = { 0 };
	int* p = (int*)malloc(sizeof(int));
	for (i = 0; i <10; i++) 
	{
		x++;
	}
	switch (c) 
	{
		case 'c':
			x++;
			break;
	}
	int returnValue = -1;
	if (x == CONSTANT_INT) 
	{
		returnValue = 1;
	}
	struct temp t;
	return returnValue;
}
/*PROBLEM*/
struct temp
{
	int something = 5;
}
/*********/
