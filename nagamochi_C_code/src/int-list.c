#include "../../include/int-list.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void ls_free(int_ls *is)
{
    is = ls_first(is);
    while (is)
    {
        int_ls *next = is->next;
        //free(is);
        is = next;
    }
}

//free anything after is
void ls_free_some(int_ls *is)
{   
    if(is && is->prev){ //but what if is->prev was just freed?
        is->prev->next=NULL;
        is->prev = NULL;
    }
    //ls_free(is);
}

int_ls *ls_create()
{
    int_ls *ghost = malloc(sizeof(int_ls));

    ghost->value = 0;

    ghost->prev = NULL;
    ghost->next = NULL;
    return ghost;
}

int_ls *ls_first(int_ls *is)
{
    if (!is)
        return is;
    while (is->prev)
        is = is->prev;
    return is;
}

int_ls *ls_last(int_ls *is)
{
    if (!is)
        return is;
    while (is->next)
        is = is->next;
    return is;
}

int ls_size(int_ls *is)
{
    is = ls_first(is);
    int n = 0;
    while (is)
    {
        n++;
        is = is->next;
    }
    return n;
}

int_ls *ls_add(int_ls *is, int i)
{
    int_ls *n = ls_create();
    n->value = i;
    n->next = is;
    if (is)
    {
        is->prev = n;
    }
    return n;
}

int_ls *ls_remove(int_ls *is)
{
    if (!is)
        return NULL;

    int_ls *is_prev = is->prev;
    int_ls *is_next = is->next;

    if (is_prev)
    {
        is_prev->next = is_next;
    }
    if (is_next)
    {
        is_next->prev = is_prev;
    }
    is->next = NULL;
    is->prev = NULL;
    //ls_free(is);

    return (is_prev) ? is_prev : is_next;
}

int ls_remove_all(int_ls *is, int i)
{
    return 0;
}

void* ls_remove_list(int_ls *is, int_ls *ns)
{   
    int_ls* xb = is;
    while(xb = ls_contains_any(is,ns)){
        is = xb = ls_remove(xb);
    }
    return is;
}

// appends js to is
int_ls *ls_merge(int_ls *is, int_ls *js)
{
    if (!is)
        return js;
    if (!js)
        return is;

    int_ls *last = ls_last(is);

    last->next = js;
    js->prev = last;
    return is;
}

void ls_print(int_ls *is)
{
    printf("{ ");
    while (is)
    {
        printf("%i ", is->value);
        is = is->next;
    }
    printf("}");
}

//copy is reversed
int_ls* ls_copy(int_ls* ls){
    int_ls* copy = NULL;

    while(ls){
        copy = ls_add(copy,ls->value);
        ls = ls->next;
    }

    return copy;
}

int_ls *ls_contains(int_ls *is, int n)
{
    while (is)
    {
        if (is->value == n)
            break;
        is = is->next;
    }
    return is;
}

int compare_int(const void *a, const void *b)
{
    return (*(int *)a - *(int *)b);
}

int ls_contains_2(int_ls *list, int a, int b)
{
    list = ls_first(list);
    int aFound = 0;
    int bFound = 0;

    while (list)
    {
        if (list->value == a)
        {
            aFound = 1;
            if (bFound)
                break;
        }
        if (list->value == b)
        {
            bFound = 1;
            if (aFound)
                break;
        }
        list = list->next;
    }

    return aFound && bFound;
}

int_ls *ls_contains_any(int_ls *list, int_ls *ns)
{
    if (list == NULL || ns == NULL)
        return 0;

    int_ls *cur_ls = list;
    while (cur_ls)
    {
        int_ls *cur_n = ns;
        while (cur_n)
        {
            if (cur_n->value == cur_ls->value)
            {
                return cur_ls;
            }
            cur_n = cur_n->next;
        }
        cur_ls = cur_ls->next;
    }
    return cur_ls;
}

/*
int ls_contains_list_bsearch(int_ls* list, int_ls* ns){
    if(list == NULL || ns == NULL)
        return 0;

    list = ls_first(list);
    ns = ls_first(ns);

    int num_len = ls_size(ns);

    printf("size: %i\n", num_len);

    int* nums = (int*)malloc(sizeof(int)*num_len);

    for(int i =0; i<num_len; i++){
        nums[i] = ns->value;
        ns = ns->next;
    }

    qsort(nums,num_len, sizeof(int), compare_int);

    int unique_nums = num_len;

    for(int i =1; i<num_len; i++){
        if( nums[i] == nums[i-1])
            unique_nums--;
    }


    int found = 0;
    char* isFound = (char*)malloc(num_len*sizeof(char));
    memset(isFound,0,sizeof(char)*num_len);

    while(list){
        int* key = &(list->value);
        void* inList = bsearch(key, nums, num_len, sizeof(int),compare_int);

        unsigned long b_index = ((int*)inList - (int*)nums)/sizeof(int);
        printf("%i @ ind = %i\n",*key,b_index);


        if(inList && !isFound[b_index]){
            found++;
            isFound[b_index] = 1;
            if(found == unique_nums)
                break;
        }
        list = list->next;
    }


    free(nums);
    free(isFound);
    return found == unique_nums;
}
*/

// void merge_set(int_ls* is, int_ls* js);

// void merge_set_fn(int_ls* is, int_ls* js);
