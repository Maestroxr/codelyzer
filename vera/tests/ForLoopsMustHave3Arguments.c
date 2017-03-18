
int main()
{

	
	int x = 0, i = 0;
	
	/*OK*/
	for (i = 0; i < 10; i++) 
	{
		x++;
	}
	
	for (int j = 0; j < 10; i++) 
	{
		j++;
	}
	/*--------*/
	
	/*PROBLEM*/
	for (i = 0; i < 10; 4) 
	{
		x++;
	}
	for (i = 0; 5 < 10; i++) 
	{
		x++;
	}
	for (; i < 10; i++)
	{
		x++;
	}
	for (i = 0; i < 10; )
	{
		x++;
	}
	/*********/
	
	
	return x;
}

