#ifndef NAGAMOCHI_H
#define NAGAMOCHI_H

#include <stdlib.h>
#include <stdio.h>
#include "../include/tree-helper.h"
#include "../include/graph.h"
#include "../include/int-list.h"
#include "../include/list.h"

typedef struct edge_ls
{
    struct edge_ls *next;
    struct edge_ls *prev;

    edge *e;
} edge_ls;

edge_ls* edge_ls_copy(edge_ls* el);

typedef struct swing_ls{
    struct swing_ls* next;
    struct swing_ls* prev;

    edge* e;

    int up;
    int down;
    int p_up;
    int p_down;

    int is_solo_edge;
    int in_lower;

    edge_ls* binding_edges;
}swing_ls;


typedef struct chain_ls{
    struct chain_ls* next;
    struct chain_ls* prev;

    int u;
    int u2;
    int uk;

    int ua;

    swing_ls* swings;
    edge_ls* binding_edges;
    edge_ls* swing_edges;

    edge* e_p; //upper
}chain_ls;

//TODO
void edge_ls_free(edge_ls* el);
//TODO
void chain_ls_free(chain_ls* ch);

chain_ls* create_chain(int u,int u2,int uk);
chain_ls* find_chains(graph* t, int v);
void process_chains(graph* g, graph* t, chain_ls* chains);

void p_ch(void* chain_ls);

void print_chain(chain_ls* chain_ls);

void print_chain_and_swings(chain_ls* chain_ls);

int_ls* branches(graph* t, int v);

edge_ls* E(graph* g, graph* t,int_ls* x);

edge* high(graph* g, graph* t, int_ls* x);

edge *nagamochi(graph *g, graph *t, double approx);

void p1(graph *g, graph *t, int u);

int case1(graph *g, graph *t);
int case2(graph *g, graph *t);

int case3(graph *g, graph *t);

int case4(graph *g, graph *t);

// accepts edge_ls* and edge*
int edge_match(void *list, void *item);

// edge_ls* graph_adjacent_edges(graph* g, int v);

void print_edge_ls_fn(void* el);
void print_edge_ls(edge_ls* el);

void edge_ls_print_vertices(edge_ls* e);

edge_ls* edge_ls_create(edge* e);

edge_ls* leaf_to_leaf_edges(graph* g, graph*t, int v);
edge_ls* leaf_edges(graph* g, graph* t, int v);

edge_ls* prime_edges_type1(graph* g, graph* t, int v);
edge_ls* prime_edges_type2(graph* g, graph* t, int v);
edge_ls* prime_edges(graph* g, graph* t, int v);

void COVER(graph* g, graph* t, int v, chain_ls* P);

void lemma9(graph* g, graph* t, int v, chain_ls* P, double approx);

int A3(graph* g, graph* t, chain_ls* P);



#endif