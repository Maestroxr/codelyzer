
int main()
{

	int x = 0;
	
	/*OK*/
	int* p1 = NULL;
	int* p2 = (int*)malloc(sizeof(int)),* p3 = NULL;
	int** p4 = (int**)malloc(sizeof(int)),***** p5 = (int*****)malloc(sizeof(int));
	
	/*--------*/
	
	/*PROBLEM*/
	int * problem1 = NULL;
	int* pp2 = (int*)malloc(sizeof(int)), * problem2 = NULL;
	int*  * problem3 = (int**)malloc(sizeof(int)),  ** *  **     * problem4 = (int******)malloc(sizeof(int));
	
	/*********/
	
	if (!p1 || !p2 || !p3 || !p4 || !p5 || !pp2 || !problem1 || !problem2 || !problem3 || !problem4 || !problem5)
	{
		x = -1;
	}
	
	return x;
}



