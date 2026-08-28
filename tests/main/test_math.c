#include "unity.h"
#include "math.h"
#include <stdio.h>

void test_add_positive_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(5, add(2, 3));
}

void test_add_negative_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(-5, add(-2, -3));
}

void test_add_zero(void)
{
    TEST_ASSERT_EQUAL_INT(5, add(5, 0));
}

void test_multiply_positive_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(6, multiply(2, 3));
}

void test_multiply_by_zero(void)
{
    TEST_ASSERT_EQUAL_INT(0, multiply(5, 0));
}

void test_multiply_negative_numbers(void)
{
    TEST_ASSERT_EQUAL_INT(-6, multiply(-2, 3));
}

void test_divide_positive_numbers(void)
{
    float result;

    TEST_ASSERT_TRUE(divide(10, 2, &result));
    TEST_ASSERT_FLOAT_WITHIN(0.001, 5.0, result);
}

void test_divide_fraction(void)
{
    float result;

    TEST_ASSERT_TRUE(divide(5, 2, &result));
    TEST_ASSERT_FLOAT_WITHIN(0.001, 2.5, result);
}

void test_divide_by_zero(void)
{
    float result;

    TEST_ASSERT_FALSE(divide(5, 0, &result));
}

void app_main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_add_positive_numbers);
    RUN_TEST(test_add_negative_numbers);
    RUN_TEST(test_add_zero);

    RUN_TEST(test_multiply_positive_numbers);
    RUN_TEST(test_multiply_by_zero);
    RUN_TEST(test_multiply_negative_numbers);

    RUN_TEST(test_divide_positive_numbers);
    RUN_TEST(test_divide_fraction);
    RUN_TEST(test_divide_by_zero);
    printf("Hil testing .........................");
    printf("Hil testing .............bye............");
    UNITY_END();
}