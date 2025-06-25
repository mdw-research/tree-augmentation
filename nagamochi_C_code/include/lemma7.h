#pragma once

#include <stdlib.h>
#include <stdio.h>
#include "../include/tree-helper.h"
#include "../include/graph.h"
#include "../include/int-list.h"
#include "../include/list.h"
#include "nagamochi.h"
#include "../include/blossom.h"




void lemma7(graph* g, graph* t, int r, double approx);

void trim_lowest_edges(graph* g, graph* t, int r, int_ls* leaves);

pair_ls* pair_ls_copy(pair_ls* ls);

void lemma7_helper(graph* g, graph* t, int r, double approx, int recur_depth, pair_ls* cur_edges);