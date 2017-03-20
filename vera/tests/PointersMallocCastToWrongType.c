
int main() 
{
	int returnValue = 0;
	
	/*OK*/
	int* p1 = (int*)malloc(sizeof(int));
	
	int*** p2 = (int***)malloc(sizeof(int)),** p3 = (int**)malloc(sizeof(int));
	
	if (!p1 || !p2)
	{
		x = -1;
	}
	
	p2 = (int***)malloc(sizeof(int));
	
	p1 = (int*)malloc(sizeof(int));
	
	
	
	/*--------*/
	
	/*PROBLEM*/
	
	int* problem1 = (char*)malloc(sizeof(int));
	int** problem2 = 0;

	
	
	problem2 = (void**)malloc(sizeof(int));
	
	
	
	int*** problem3 = (int*)malloc(sizeof(int));
	if (!problem3)
	{
		x = -1;
	}
	problem3 = (int)malloc(sizeof(int));
	
	
	int**** problem4 = (void****)malloc(sizeof(int)),***** problem5 = (int******)malloc(sizeof(int));
	

	/*********/
	
	if (!p1 || !p2 || !p3 || !problem1 || !problem2 || !problem3 || !problem4 || !problem5)
	{
		x = -1;
	}

	
}


