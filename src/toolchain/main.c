#include <stdio.h>
#include "demo.h"

/* Written for this experiment. The bounded domain avoids signed overflow. */
static int scale_and_bias(int x)
{
    return SCALE * x + BIAS;
}

int alternating_sum(int n)
{
    int sum = 0;
    for (int i = 0; i < n; ++i) {
        int term = scale_and_bias(i);
        if (i % 2 == 0) {
            sum += term;
        } else {
            sum -= term;
        }
    }
    return sum;
}

int main(void)
{
    int n;
    if (scanf("%d", &n) != 1) {
        fputs("expected one integer\n", stderr);
        return 1;
    }
    if (n < 0 || n > MAX_N) {
        fputs("n must be in [0, 20]\n", stderr);
        return 2;
    }
    int sum = alternating_sum(n);
    int adjusted = add_bonus(sum);
    printf("n=%d alternating=%d adjusted=%d\n", n, sum, adjusted);
    return 0;
}
