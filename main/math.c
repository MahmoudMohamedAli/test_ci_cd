#include "math.h"

int add(int a, int b)
{
    return a + b;
}

int multiply(int a, int b)
{
    return a * b;
}

bool divide(int a, int b, float *result)
{
    if (b == 0) {
        return false;
    }

    *result = (float)a / b;
    return true;
}