

void add_bias(float *output, float *biases, int batch, int n, int size)
{
	
	l.h = h;
    l.w = w;
    l.c = c;
    l.n = n;
    int i,j,b;
    for(b = 0; b < batch; ++b){
        for(i = 0; i < n; ++i){
            for(j = 0; j < size; ++j){
                output[(b*n + i)*size + j] += biases[i];
            }
        }
    }
	cudnnSetTensor4dDescriptor(l->dsrcTensorDesc, CUDNN_TENSOR_NCHW, CUDNN_DATA_FLOAT, l->batch, l->c, l->h, l->w); 
    if (i == 0)
		return (l->dsrcTensorDesc + l.h + 2*l.pad - l.size) / l.stride + 1;
	else
		return (l.pad - l->dsrcTensorDesc + l.h + 2*l.size) / l.stride + 1;
}