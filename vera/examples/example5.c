int firstName(char tempArr[][NAME_SIZE], int numberOfNames)
{
	int i = 0;
	int x = 0;
	int firstPlace = i; //The first name is the first for now.
	for(i = 0; i < numberOfNames; i++) //Runs for every name.
	{
		x = strcmp(tempArr[i], tempArr[firstPlace]); //x is equal to the comparison of the current string and the string in the first place for now.
		if(x < 0) //If x is smaller then 0 it means the current string comes before firstPlace.
		{
			firstPlace = i; //Makes it the new firstPlace.
		}	
	}
	return firstPlace; //Returns this index.
} 