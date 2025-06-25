#include "../../include/list.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void *l_first(void *list)
{
    ls *is = list;
    if (!is)
        return is;
    while (is->prev)
        is = is->prev;
    return is;
}

void *l_last(void *list)
{
    ls *is = list;
    if (!is)
        return is;
    while (is->next)
        is = is->next;
    return is;
}

int l_size(void *list)
{
    ls *is = list;
    is = l_first(is);
    int n = 0;
    while (is)
    {
        n++;
        is = is->next;
    }
    return n;
}

void *l_add(void *list, void *new_list)
{
    ls *is = list;
    ls *new = new_list;
    if (!new)
        return NULL;
    new->next = is;
    if (is)
    {
        new->prev = is->prev;
        is->prev = new;
    }
    return new;
}

//removes the node
void *l_remove(void *list)
{
    ls *is = list;
    if (!is)
        return NULL;

    ls *is_prev = is->prev;
    ls *is_next = is->next;

    if (is_prev)
    {
        is_prev->next = is_next;
    }
    if (is_next)
    {
        is_next->prev = is_prev;
    }
    //free(is);
    return (is_prev) ? is_prev : is_next;
}

void *l_merge(void *list1, void *list2)
{
    ls *l = l_first(list1);
    ls *l2 = l_first(list2);
    if (!l)
        return l2;
    if (!l2)
        return l;

    ls *last = l_last(l);

    last->next = l2;
    l2->prev = last;
    return l;
}

void *l_contains(void *list, int (*match)(void *, void *), void *item)
{
    ls *l = list;
    while (l)
    {
        if (match(l, item))
        {
            return l;
        }
        l = l->next;
    }
    return NULL;
}

void *l_contains_ls(void *list, int (*match)(void *, void *), void *items)
{
    ls *l = list;
    while (l)
    {
        ls *item_ls = items;
        while (item_ls)
        {
            if (match(l, item_ls))
            {
                return l;
            }
            item_ls = item_ls->next;
        }
        l = l->next;
    }
    return NULL;
}

//removes all
void *l_remove_item(void *list, int (*match)(void *, void *), void *item)
{
    void *rm = list;
    while (rm = l_contains(rm, match, item))
    {
        if (rm == list)
        {
            ls *ll = list;
            list = (ll->next) ? ll->next : ll->prev;
        }
        rm = l_remove(rm);
    }
    return list;
}

void *l_remove_ls(void *list, int (*match)(void *, void *), void *items)
{
    void *rm = list;
    while (rm = l_contains_ls(rm, match, items))
    {
        if (rm == list)
        {
            ls *ll = list;
            list = (ll->next) ? ll->next : ll->prev;
        }
        rm = l_remove(rm);
    }
    return list;
}

void l_print(void *list, void (*print_fn)(void *))
{
    ls *l = list;
    printf("{ ");
    while (l)
    {
        print_fn(l);
        printf(" ");
        l = l->next;
    }
    printf(" }");
}


void l_free_some(){

}

void l_free_recursive(void* l){
    if(!l)
        return;
    l_free_recursive((void*)(((ls*)l)->next));
    //free(l);
    return;
}

void l_free(void* l){
    ls* ll = l_first(l);
    l_free_recursive(ll);
    return;
    while(ll){
        ls* next = ll->next;
        //free(ll);
        ll = next;
    }
}



void l_free_fn(){

}