#include <stdio.h>
#include <stdbool.h>

bool can_divide(int w);

int main(void)
{
    int w;
    scanf("%d", &w);

    char* str_output;
    switch (can_divide(w))
    {
        case false:
            str_output = "NO";
            break;
        case true:
            str_output = "YES";
            break;
    }

    printf(str_output);
}

bool can_divide(int w)
{
    return w > 2 && w % 2 == 0;
}