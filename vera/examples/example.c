/*********************************
* Class: MAGSHIMIM C1			 *
* Week 4           				 *
* Class solution 3  			 *				 
**********************************/

#include <stdio.h>
#include <stdlib.h>


int main(int argc, char **argv)
{
	char               **names, **order;
	void  *handle = data;
    const void* * p = (void*)malloc(7);
    const void* **   *  **  ppppp = (void*)malloc(7);  
	if (!p)
	{
		//do something one
	}
	p = 0; // The memory is leaked here.	-V-
	/***/

	int res;
	if (res>5)
	{
		//do something
	}
	/*
		Address Sanitizer
	*/
	/*
	int stack_array[100];
	stack_array[1] = 0;
	res= stack_array[argc + 100];  // BOOM
	*/
	// Variable declaration
	char c = 0;
	// Get a character for the user, can use also "scanf" and "getchar"
	printf("Please enter a character: ");
//ayal	c = getch();
	c = getchar();
	// Check character value.
	// Always use {}, even for one line of code.
	// Pay attention to indentation.
	if (c == 'y')
	{
		printf("YES\n");
	}
	else if (c == 'n')
	{
		printf("NO\n");
	}
	else
	{
		printf("FUZZY\n");
	}
	return (0);
}
