#include <stdio.h>
#include <time.h>
#include <math.h>
#include <string.h>
#define NINE 9 
#define EIGHT 8
#define SIX 6
#define NINETY_SIX 96
#define O_H_A_T_T 123
#define SIXTY_FOUR 64
#define NINETY_ONE 91
#define FORTY_SEVEN 47
#define FIFTY_EIGHT 58
int chek(char password[]);
int oneNumber(char password[]);
int oneBig(char password[]);
int oneLittle(char password[]);
int continuousCharacter(char password[]);

int main(void)
{
	char password[NINE] = {0};
	printf("Enter a password: ");
	fgets(password , 9 , stdin);
	if (chek(password))
	{
		printf("Valid Password");
	}
	else
	{
		printf("Invalid Password");
	}
	return (0);
}

/*
Function that checks whether a valid password or not
input: the password
output: 1 - yes , 0 - one
*/
int chek(char password[])
{
	if(strlen(password)>= SIX && strlen(password) <= EIGHT)
	{
		if(oneNumber(password) == 1 && oneBig(password) == 1 && oneLittle(password) == 1 && continuousCharacter(password) == 1)
		{
			return 1;
		}
		else
		{
			return 0;
		}
	}
	return 0;
}
/*
Function that checks if there is at least one number via password
input: thr password
output: 1 - yes , 0 - one
*/
int oneNumber(char password[])
{
	int i = 0;
	for(i = 0 ; i < strlen(password) ; i++)
	{
		if(password[i] >FORTY_SEVEN && password[i] < FIFTY_EIGHT )
		{
			return 1;
		}
	}
	return 0;
}

/*
Function that checks if there is at least one upper case letter via password
input: thr password
output: 1 - yes , 0 - one
*/
int oneBig(char password[])
{
	int i = 0;
	for(i = 0 ; i < strlen(password) ; i++)
	{
		if(password[i] >NINETY_SIX && password[i] < O_H_A_T_T)
		{
			return 1;
		}
	}
	return 0;
}

/*
Function that checks if there is at least one small sign via password
input: thr password
output: 1 - yes , 0 - one
*/
int oneLittle(char password[])
{
	int i = 0;
	for(i = 0 ; i < strlen(password) ; i++)
	{
		if( password[i] >SIXTY_FOUR && password[i] < NINETY_ONE  )
		{
			return 1;
		}
	}
	return 0;
}

/*
Function that checks if there is the same character twice in a row
input: the password
output: 0 - yes , 1 - no
*/
int continuousCharacter(char password[])
{
	int i = 0;
	for(i = 0 ; i < strlen(password) ; i++)
	{
		if(password[i] == password[i+1])
		{
			return 0;
		}
	}
	return 1;
}

