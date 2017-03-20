/*********************************
* Class: MAGSHIMIM C2			 *
* Week 3           				 *
* HW solution   			 	 *
**********************************/
#include <stdio.h>
#include <string.h>

#define STR_LEN 50
#define ASCII_LITTLE_A 'a'
#define ABC_SIZE 26

void myFgets(char str[], int n);
void decrypt(char* encText, int n);
void swap(char* a, char* b);

int main(void)
{
	char cipher[STR_LEN] = {0};
	int key = 0;
	printf("Enter cipher to decrypt: ");
	myFgets(cipher, STR_LEN);
	printf("Enter decryption key: ");
	scanf("%d", &key);
	decrypt(cipher,key);
	printf("Decrypted text: ");
	puts(cipher);
	return 0;
}

/**
The function decrypts a text. It has two steps:
step1 - Flip the text from end to beginning.
step2 - Apply modulo operator.

Input:
	encText - string of encrypted text
	n - key for the modulo operation
*/
void decrypt(char* encText, int n)
{
	int i = 0, len = strlen(encText);
	// reverse the string.	
	// easier way - the non-standard function: strrev(encText);
	for(i = 0; i < len / 2; i++ )
	{
		swap(encText + i, encText + len - 1 - i);	
	}	
	
	for(i = 0; i < len; i++)
	{
		*(encText + i) = ((*(encText + i) - ASCII_LITTLE_A) + n) % ABC_SIZE + ASCII_LITTLE_A;
	}
}


/*
Function will perform the fgets command and also remove the newline 
that might be at the end of the string - a known issue with fgets.
input: the buffer to read into, the number of chars to read
*/
void myFgets(char str[], int n)
{
	fgets(str, n, stdin);
	str[strcspn(str, "\n")] = 0;
}

/*
Function swaps two chars. 
input: the chars to swap
output: none
*/
void swap(char* a, char* b)
{
	char t = *a;
	*a = *b;
	*b = t;
}

