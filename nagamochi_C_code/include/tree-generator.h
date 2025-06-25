#ifndef TREE_GENERATOR_H
#define TREE_GENERATOR_H
#include "./graph.h"

/* generate a linear tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* linearTree(int n);

/* generate a star tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* starTree(int n);

/* generates a star-like tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* starlikeTree(int n);

/* generates a caterpillar tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* caterpillarTree(int n);

/* generates a lobster tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* lobsterTree(int n);

/* generate a random forest
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* randomForestTree(int n);

graph* createEdgeSet(int density, graph* tree);

#endif
