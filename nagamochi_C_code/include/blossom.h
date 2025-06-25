#ifndef BLOSSOM_H
#define BLOSSOM_H

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "../include/tree-helper.h"
#include "../include/graph.h"
#include "../include/int-list.h"
#include "../include/list.h"
#include "../include/nagamochi.h"


typedef struct pair_ls
{
    struct pair_ls *next;
    struct pair_ls *prev;

    int u;
    int v;

    int blossom_number;
} pair_ls;

int edge_match(void *list, void *item);
int edge_ls_match(void *list, void *item);
int edge_match_one(void *list, void *item);
edge_ls* edge_ls_contains(edge_ls* el, edge* e);

pair_ls* pair_create(int u, int v, int blossom_number);

pair_ls* blossom_merge(graph* g, int u, int v, int blossom_number, pair_ls* merge_order);

pair_ls* blossom_unmerge(graph* g, pair_ls* merge_order);

pair_ls* blossom_unmerge_2(graph* g, pair_ls* merge_order);

int_ls* last_blossom_verts(pair_ls* merge_order);

// computes maximum matching
edge_ls* blossom_algorithm(graph *g, int_ls *vs);

pair_ls* lift_blossom2(graph* g, edge_ls* matching, int* queued_by, int* queues, char* not_exposed, edge_ls* es, pair_ls* merge_order);

edge_ls *blossom_algorithm2(graph *g, int_ls *vs, edge_ls* es);

void set_gm(graph* g);
void set_tm(graph* g);
#endif