
int main() 
{
	
	
	/*OK*/
	int i = 0, x = 0;
	{
		;
		;
		{
			;
			;
		}
	}	
	for (i = 0; i <10; i++) 
	{
		x++;
	}
	for (i = 0; i <10; i++) {x++;}
	/*--------*/
	
	/*PROBLEM*/
	int j = 0;;
	;;
	{
		;;
		{
			;;
		}
	}
	for (i = 0; i <10; i++) 
	{
		x++;;
	}
	for (i = 0; i <10; i++) {x++;;}
	/*********/
	
}


