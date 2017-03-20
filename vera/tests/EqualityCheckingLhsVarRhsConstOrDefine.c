
#define CONSTANT_DEFINE 0
int main()
{
	int returnValue = 0;
	
	const int CONSTANT_INT = 0;
	int x = 0;
	
	/*OK*/
	if (CONSTANT_INT == x) 
	{
		returnValue = 1;
	}
	
	if (CONSTANT_DEFINE == x) 
	{
		returnValue = 1;
	}
	
	if (CONSTANT_DEFINE == CONSTANT_INT) 
	{
		returnValue = 1;
	}
	
	if (CONSTANT_INT == CONSTANT_DEFINE) 
	{
		returnValue = 1;
	}
	/*--------*/
	
	int problem1 = 0;
	/*PROBLEM*/
	if (problem1 == CONSTANT_INT) 
	{
		returnValue = -1;
	}
	int problem2 = 0;
	if (problem2 == CONSTANT_DEFINE) 
	{
		returnValue = -1;
	}
	/*--------*/
	
	
	return returnValue;
}

