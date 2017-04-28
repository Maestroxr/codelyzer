int* ptr = 0;
void functionThatEscapesLocalObject() 
{
	int local[ 100 ] = { 0 };
	ptr = &local[ 0 ];
}
int main(int argc, char **argv) 
{
	functionThatEscapesLocalObject();
	return ptr[ argc ];
}