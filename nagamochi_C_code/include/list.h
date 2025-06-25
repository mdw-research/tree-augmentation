
#ifndef LLIST
#define LLIST

typedef struct ls
{
    struct ls *next;
    struct ls *prev;
} ls;

void *l_create();
void *l_first(void *list);
void *l_last(void *l);

void *l_add(void *l, void *l2);

void *l_merge(void *l, void *l2);


int l_size(void *list);
void l_print(void *l, void (*print_fn)(void *));

void *l_contains(void *l, int (*compare)(void *, void *), void *item);
void *l_contains_ls(void *l, int (*compare)(void *, void *), void *items);

void *l_remove(void *l);
void *l_remove_item(void *list, int (*match)(void *, void *), void *item);
void *l_remove_ls(void *list, int (*match)(void *, void *), void *items);
void l_free(void* l);
#endif