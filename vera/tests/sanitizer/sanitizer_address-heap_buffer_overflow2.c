/*********************************
* Class: MAGSHIMIM C2			 *
* Week 5              			 *
**********************************/

#include <stdio.h>
#include <stdlib.h>
void valueScan(int * pArr, int size);
void arrSort(int *pArr, int size);
void arrPrint(int **pArr,int rows);
void prog(int **pArr, int rows);
void arrOrder(int **pArr, int rows);
int main(void)
{
	int **pArr = 0;
	int rows = 0;
	printf("How many rows do you want in the array?");
	scanf("%d", &rows);
	pArr = (int**)malloc(sizeof(int)*rows); //saving a 2d array on the heap.
	prog(pArr,rows);
	
	getchar();	
	return 0;
}
/*
Function that calls other functions to sort and print.also saving arrays on the heap.
input:pointer to the 2d array and number of rows
output:none
*/
void prog(int **pArr,int rows)
{
	int i = 0;
	int j = 0;
	int size = 0;
	for (i = 0; i < rows; i++)
	{
		printf("Enter length of array %d:", i);
		scanf("%d", &size);
		*(pArr + i) = (int *)malloc(sizeof(int)*size); //saving arrays on the 2d array at the heap.
		valueScan(*(pArr + i), size);//sending the arrays to get filled by values from the user.
	}
	arrPrint(pArr,rows);//first print
	for (i = 0; i < rows; i++)
	{
		arrSort(*(pArr + i), pArr[i][0]);//sending arrays by order to sort.
	}
	printf("\nSorted:\n");
	arrPrint(pArr, rows);//print after sorted.
	arrOrder(pArr, rows);//sending the arrays to get in the correct order by big and small.
	printf("\nOrdered:\n");
	arrPrint(pArr, rows);//prints after correct order.
	
}
/*
Function that gets an array by pointer and scaning values to it
input:array and his size.
output:none.
*/
void valueScan(int * pArr, int size)
{
	int i = 0;
	int j =0;
	pArr[0] = size;
	for (i = 1; i <= size; i++)
	{
		printf("Enter value:");
		scanf("%d", (pArr + i));
	}

}
/*
Function that sorting an array from the smallest value to the largest.
input:the array and his size.
output:none
*/
void arrSort(int *pArr, int size)
{
	int temp = 0;
	int i = 1;
	int j = 0;
	for (i = 1; i <= size; i++)
	{
		for (j = i + 1; j <= size; j++)
		{
			if (pArr[i] > pArr[j])
			{
				temp = pArr[i];
				pArr[i] = pArr[j];//switching values
				pArr[j] = temp;
			}
		}
	}
}
/*
Function that prints the arrays.
input:pointer to the 2d array and number of arrays in it.
output:none.
*/
void arrPrint(int **pArr,int rows)
{
	int i = 0;
	int j = 0;
	for (i = 0; i <rows; i++)
	{
		for (j = 1; j <=pArr[i][0]; j++)
		{
			printf("%d ", pArr[i][j]);
		}
		printf("\n");
	}
}
/*
Function that puting the arrays in order from the shortest to the longest
input:pointer to the 2d array and number of rows
output:none
*/
void arrOrder(int **pArr, int rows)
{
	int i = 0;
	int j = 0;
	int *pTemp = 0;
	for (i = 0; i < rows; i++)
	{
		for (j = i + 1; j < rows;j++)
		{ 
			if (pArr[i][0] > pArr[j][0])//checking who is longer by his first value (in this case it tells the length of the array)
			{
				pTemp = pArr[j];
				pArr[j] = pArr[i];
				pArr[i] = pTemp;

			}
		}
	}
}