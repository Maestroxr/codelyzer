
int main() 
{
	int returnValue = 0;
	
	/*OK*/
	int* p1 = (int*)malloc(sizeof(int));
	if (!p1)
	{
		returnValue = -1;
	}
	int* p2 = (int*)malloc(sizeof(int));
	if (p2 != NULL)
	{
		returnValue = 2;
	}
	p2 = (int*)malloc(sizeof(int));
	if (NULL != p2)
	{
		returnValue = 2;
	}
	p1 = (int*)malloc(sizeof(int));
	if (NULL == p1)
	{
		returnValue = -1;
	}
	int* p3 = (int*)malloc(sizeof(int));
	if (p3 == NULL)
	{
		returnValue = -12;
	}
	/*--------*/
	
	/*PROBLEM*/
	
	if (!p1)
	{
		returnValue = -1;
	}
	p1 = (int*)malloc(sizeof(int));
	
	
	p2 = (int*)malloc(sizeof(int));
	if (p3 != NULL)
	{
		returnValue = 2;
	}
	
	p3 = (int*)malloc(sizeof(int));
	p3 = (int*)malloc(sizeof(int));
	if (p3 == NULL)
	{
		returnValue = -12;
	}
	
	int* p4 = (int*)malloc(sizeof(int));

	/*********/
	
}


