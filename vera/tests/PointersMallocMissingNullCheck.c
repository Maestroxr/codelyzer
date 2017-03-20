
int main() 
{
	int returnValue = 0;
	
	/*OK*/
	int* p1 = (int*)malloc(sizeof(int));
	if (!p1)
	{
		returnValue = -1;
	}
	int* p2 = (int*)malloc(sizeof(int)),* p3 = (int*)malloc(sizeof(int));
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
	
	if (p3 == NULL)
	{
		returnValue = -12;
	}
	if (NULL == p1)
	{
		returnValue = -1;
	}
	/*--------*/
	
	/*PROBLEM*/
	
	int* problem1 = (int*)malloc(sizeof(int));
	int* problem2 = 0;
	if (!problem2)
	{
		returnValue = -1;
	}
	problem2 = (int*)malloc(sizeof(int));
	
	
	
	int* problem3 = (int*)malloc(sizeof(int));
	problem3 = (int*)malloc(sizeof(int));
	if (problem3 == NULL)
	{
		returnValue = -12;
	}
	
	int* problem4 = (int*)malloc(sizeof(int)),* problem5 = (int*)malloc(sizeof(int));
	

	/*********/
	
}


