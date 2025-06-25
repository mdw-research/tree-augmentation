#ifndef TREE_HELPER_H
#define TREE_HELPER_H
#include "graph.h"

/* prints an adjacency matrix
   n is the number of nodes in the tree
   tree is the adjacency matrix of size n x n */
void printTreeAdjMat(int n, int tree[][n]);

/* prints an adjacency matrix with padding
   n is the number of nodes in the tree
   tree is the adjacency matrix of size n x n */
void printTreeAdjMatWithPadding(int n, int tree[][n], int padding);
void printVertexCover(int n, int tree[][n], int vertex[n]);
void printMinCover(int n, int tree[][n], int vertex[n]);
int treeCover(int n, int tree[][n], int v,int stor[n][2], int covered, int vertex[n]);
void genVertexWeights(int n, int vertex[n], int max);
void genPlot(int numAlgorithms, int size, int timeSize, double times[][timeSize], int treeSize[]);

/* Generates an edge weights for a set of edges
   n is the number of nodes in the graph
   edges is the adjacency matrix of a graph of size n x n
   edgeWeights is the adjacency matrix with weights corresponding to edges of size n x n */
void genEdgeWeights(int n, int edges[][n], int edgeWeights[][n], int max);

/* Generates an edge set for tree augmentation
   n is the number of nodes in the tree
   tree is the adjacency matrix of a tree of size n x n
   edgeSet is the adjacency matrix of the edge set for tree augmentation of size n x n */
//void createEdgeSet(int n, graph* tree, graph* edgeSet);

/* Copies an adjacency matrix to another matrix of the same size
   n is the size of the adjacency matrix
   originalMatrix is the matrix to be copied from
   copyMatrix is the matrix to be copied to */
void copyMatrix(int n, int originalMatrix[][n], int copyMatrix[][n]);

/* Creates an adjacency matrix with a zero diagonal and one everywhere else
   n is the number of nodes in the graph
   completeDirectedGraph is the adjacency matrix of a graph of size n x n */
void createCompleteDirectedTree(int n, int completeDirectedGraph[][n]);

/* returns 1 if the graph is 2-edge connected, 0 otherwise */
int checkConnected(int n, graph* tree, graph* edges);

#endif
