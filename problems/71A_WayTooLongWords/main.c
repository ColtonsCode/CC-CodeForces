#include <stdio.h>
#include <string.h>

void abbreviate(char buffer[], size_t size)
{

}

int main(void)
{
    int n; // n lines, which have one word each.
    scanf("%d", &n);

    char str[101];
    for (int i = 0; i <= n; ++i)
    {
        fgets(str, sizeof(str), stdin);

        // For each word:
        if (strlen(str) > 10)
        {
            abbreviate(str, sizeof(str));
        }

        printf("%s", str);
    }

    return 0;
}