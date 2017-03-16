#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#define NUMBER_OF_NAMES 10
#define NAME_SIZE 50

void scanNames(char tempArr[][NAME_SIZE], int nameSize);
int longestName(char tempArr[][NAME_SIZE], int numberOfNames);
int shortestName(char tempArr[][NAME_SIZE], int numberOfNames);
int firstName(char tempArr[][NAME_SIZE], int numberOfNames);
int lastName(char tempArr[][NAME_SIZE], int numberOfNames);

int main(void)
{
	char names[NUMBER_OF_NAMES][NAME_SIZE] = { 0 };
	scanNames(names, NUMBER_OF_NAMES); //Calls this function with the 2D array names[][] and NUMBER_OF_NAMES as an input.
	printf("\nShortest: %s\n", names[shortestName(names, NUMBER_OF_NAMES)]); //Prints the output of this function.
	printf("Longest: %s\n", names[longestName(names, NUMBER_OF_NAMES)]); //Prints the output of this function.
	printf("First: %s\n", names[firstName(names, NUMBER_OF_NAMES)]); //Prints the output of this function.
	printf("Last: %s\n", names[lastName(names, NUMBER_OF_NAMES)]); //Prints the output of this function.
	return 0; //Returns zero.
}

/*
This function will scan 10 names from the user and will enter them to the 2D array names[][].
INPUT: The 2D array names[][] and the number of names it can fill.
OUTPUT: None.
*/
void scanNames(char tempArr[][NAME_SIZE], int numberOfNames)
{
	int i;
	printf("Enter 10 names:\n"); //A message for the user.
	for(i = 0; i < numberOfNames; i++) //Runs for every name.
	{
		fgets(tempArr[i], NAME_SIZE, stdin); //Scans a string from the keyboard to the current index.
		tempArr[i][strlen(tempArr[i]) - 1] = 0; //Deletes the \n.
	}
}

/*
This function will check with name is the longest and will return its index.
INPUT: The 2D array names[][] and the number of names it can fill.
OUTPUT: The index of the longest name.
*/
int longestName(char tempArr[][NAME_SIZE], int numberOfNames)
{
	int i;
	int longest = strlen(tempArr[i]); //The longest name for now is the first name.
	int place = 0;
	for(i = 0; i < numberOfNames; i++) //Runs for every name.
	{
		if(strlen(tempArr[i]) > longest) //If the current name is longer then the last longest name.
		{
			longest = strlen(tempArr[i]); //The longest name is the new one.
			place = i; //We remeber the place of that name.
		}
	}
	return place; //Returns the index.
}

/*
This function will check with name is the shortest and will return its index.
INPUT: The 2D array names[][] and the number of names it can fill.
OUTPUT: The index of the shortest name.
*/
int shortestName(char tempArr[][NAME_SIZE], int numberOfNames)
{
	int i = 0;
	int shortest = strlen(tempArr[i]); //The shortest name for now is the first name.
	int place = 0;
	for(i = 0; i < numberOfNames; i++) //Runs for every name.
	{
		if(strlen(tempArr[i]) < shortest) //If the current name is shorter then the last shortest name.
		{
			shortest = strlen(tempArr[i]); //The shortest name is the new one.
			place = i; //We remeber the place of that name.
		}
	}
	return place; //Returns the index.
}

/*
This function will find the first name in the dictionary and will return the index it's in.
INPUT: The 2D array names[][] and the number of names it can fill.
OUTPUT: The index that the first name in the dictionary is at.
*/
int firstName(char tempArr[][NAME_SIZE], int numberOfNames)
{
	int i = 0;
	int x = 0;
	int firstPlace = i; //The first name is the first for now.
	for(i = 0; i < numberOfNames; i++) //Runs for every name.
	{
		x = strcmp(tempArr[i], tempArr[firstPlace]); //x is equal to the comparison of the current string and the string in the first place for now.
		if(x < 0) firstPlace = tempArr[i]; //Makes it the new firstPlace.
			//If x is smaller then 0 it means the current string comes before firstPlace.
		
			
			
	}
	return firstPlace; //Returns this index.
} 

/*
This function will find the last name in the dictionary and will return the index it's in.
INPUT: The 2D array names[][] and the number of names it can fill.
OUTPUT: The index that the last name in the dictionary is at.
*/
int lastName(char tempArr[][NAME_SIZE], int numberOfNames)
{
	int i = 0;
	int x = 0;
	int lastPlace = i; //The first name is the last for now.
	for(i = 0; i < numberOfNames; i++) //Runs for every name.
	{
		x = strcmp(tempArr[i], tempArr[lastPlace]); //x is equal to the comparison of the current string and the string in the last place for now.
		if(x > 0) //If x is bigger then 0 it means the current string comes after lastPlace.
		{
			lastPlace = i; //Makes it the new lastPlace.
		}	
	}
	return lastPlace; //Returns this index.
}
