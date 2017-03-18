
int main()
{

	int x = 0;
	
	/*OK*/
	int* p1 = NULL;
	int* p2 = (int*)malloc(sizeof(int));
	int** p3 = (int**)malloc(sizeof(int)),***** p4 = (int*****)malloc(sizeof(int));
	/*--------*/
	
	/*PROBLEM*/
	int*  problem1 = NULL;
	int* pp2 = NULL,*problem2 = NULL;
	int**     p3 = (int**)malloc(sizeof(int)),*****            p4 = (int*****)malloc(sizeof(int));

	/*********/
	return x;
}



