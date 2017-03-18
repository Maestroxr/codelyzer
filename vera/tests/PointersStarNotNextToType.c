
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
	int*  * p4 = (int**)malloc(sizeof(int)),  ** *  **     * p5 = (int******)malloc(sizeof(int));
	
	/*********/
	return x;
}



