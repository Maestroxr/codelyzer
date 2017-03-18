
int main()
{

	
	int i = 0;
	
	/*OK*/
	if (i>10)
	{
		x++;
	}		
	for (i = 0; i <10; i++) 
	{
		x++;
	}
	while (i<100) 
	{
		i++;
	}
	/*--------*/
	
	/*PROBLEM*/
	if (i>10) x++;
	for (i = 0; i <10; i++) x++;
	while (i<100) i++;
	/*********/
	
	
	return x;
}



