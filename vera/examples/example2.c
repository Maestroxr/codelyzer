#include <stdio.h>

int main (void)
{
	char answer = 'a';
	printf("Please enter a character: ");
	scanf("%c", &answer);
	getchar();
	switch(answer) //using the commend switch we check the char that is in answer and check which case will be true for it.
	{
		case 'y':
		printf("YES");
		break;
		case 'n':
		printf("NO");
		break;
		default:
		printf("FUZZY");
		break;
	}
	return 0;
}