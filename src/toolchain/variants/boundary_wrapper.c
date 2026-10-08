#include <stdio.h>
#include "demo.h"

/* The linker wraps only the startup reference to main. The experiment's
 * unmodified main.o supplies the externally visible alternating_sum body. */
int __wrap_main(void)
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
