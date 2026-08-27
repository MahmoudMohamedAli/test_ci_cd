#include <assert.h>
#include <stdio.h>
#include "math.h"

void test_add(void)
{
    assert(add(2, 3) == 5);
    assert(add(0, 5) == 5);
    assert(add(-2, 5) == 3);
    assert(add(-2, -3) == -5);

    printf("test_add: PASS\n");
}

void test_multiply(void)
{
    assert(multiply(2, 3) == 6);
    assert(multiply(5, 0) == 0);
    assert(multiply(-2, 3) == -6);
    assert(multiply(-2, -3) == 6);

    printf("test_multiply: PASS\n");
}


int main(void)
{
    test_add();
    test_multiply();
    printf("ALL TESTS PASSED\n");

    return 0;
}