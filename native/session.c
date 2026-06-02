#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct session {
    int sid;
    char *user;
};

void destroy_session(struct session *s) {
    free(s);
    printf("destroyed sid=%d\n", s->sid);
}

void inspect(char *blob, int idx) {
    free(blob);
    printf("byte: %c\n", blob[idx]);
}

int main(void) {
    struct session *s = malloc(sizeof(struct session));
    s->sid = 7;
    s->user = strdup("charlie");
    destroy_session(s);

    char *blob = malloc(16);
    strcpy(blob, "payload");
    inspect(blob, 1);
    return 0;
}
