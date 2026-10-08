#include "demo.h"

/* A separate translation unit makes link-time symbol resolution visible. */
int add_bonus(int value)
{
    return value + FINAL_BONUS;
}
