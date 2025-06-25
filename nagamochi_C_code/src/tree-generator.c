#include <stdlib.h>
#include <stdio.h>
#include "../include/graph.h"

/* generate a linear tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* linearTree(int n) {
  graph* g = graph_create(n);
  for (int i = 0; i < n - 1; i++) {
    graph_add_edge(g, i, i + 1);
  }
  return g;
}

/* generate a star tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* starTree(int n) {
  graph* g = graph_create(n);
  for (int i = 1; i < n; i++) {
    graph_add_edge(g, 0+1, i+1);
  }
  return g;
}

/* generates a star-like tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* starlikeTree(int n) {
  int bfactor = rand() % 101;
  graph* g = graph_create(n);
  for (int i = 1; i < n; i++) {
    if (rand() % 100 < bfactor) {
      graph_add_edge(g, 0+1, i+1);
    } else {
      graph_add_edge(g, i -1 + 1, i+1);
    }
  }
  return g;
}

/* generates a caterpillar tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* caterpillarTree(int n) {
  graph* g = graph_create(n);
  int l = rand() % n + 1;
  for (int i = 0; i < l - 1; i++) {
    graph_add_edge(g, i+1, i + 2);
  }
  for (int i = l; i < n; i++) {
    graph_add_edge(g, rand() % l+1, i+1);
  }
  return g;
}

/* generates a lobster tree
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* lobsterTree(int n) {
  graph* g = graph_create(n);
  int l = rand() % n + 1;
  int l1 = rand() % (n - l + 1) + 1;
  for (int i = 0; i < l - 1; i++) {
    graph_add_edge(g, i+1, i + 1+1);
  }
  for (int i = l; i < l + l1; i++) {
    graph_add_edge(g, rand() % l+1, i+1);
  }
  for (int i = l + l1; i < n; i++) {
    graph_add_edge(g, rand() % l1 + l+1, i+1);
  }
  return g;
}

/* generate a random forest
   n is the number of nodes
   tree is the adjacency matrix of size n x n */
graph* randomForestTree(int n) {
  graph* g = graph_create(n);
  int prufer[n - 2];
  int degree[n];

  for (int i = 0; i < n - 2; i++) {
    prufer[i] = rand() % n;
  }
  for (int i = 0; i < n; i++) {
    degree[i] = 1;
  }
  for (int i = 0; i < n - 2; i++) {
    degree[prufer[i]]++;
  }

  for (int i = 0; i < n - 2; i++) {
    for (int j = 0; j < n; j++) {
      if (degree[j] == 1) {
        graph_add_edge(g, prufer[i]+1, j+1);
        degree[prufer[i]]--;
        degree[j]--;
        break;
      }
    }
  }

  int u = -1;
  int v = -1;
  for (int i = 0; i < n; i++) {
    if (degree[i] == 1) {
      if (u == -1) {
        u = i;
      } else {
        v = i;
        break;
      }
    }
  }
  graph_add_edge(g, u+1, v+1);
  set_root(g, 1);
  return g;
}

/* This creates a set of edges based on a specified tree and density.
      If you want to make sure the edges generated are valid, wrap the generation in a loop
      that uses the function checkConnected.
   int density: a number between 0 - 100 that is the percent density of the edge set
      100 represents 100.0% chance to add an edge, 50 represents 50.0%, etc.
   graph* tree: the tree the edge set is based off of
   graph* edgeSet: an empty graph that is the same size as tree */
graph* createEdgeSet(int density, graph* tree) {
  graph* edgeset = graph_create(tree->original_vertex_count);
   for (int u = 1; u <= tree->original_vertex_count; u++) {
      for (int v = 1; v <= tree->original_vertex_count; v++) {
         if (rand() % 100 < density && u != v) {
            graph_add_edge(edgeset, u, v);
         }
      }
   }
   return edgeset;
}
/*
// Generates an edge set based off tree 
               printf("Generating Edge Set based off tree...\n");
               int maxAttempts = 100;
               int attempts = 0;
               do {
                  printf("\tAttempting to generate valid edge set...\n");
                  createEdgeSet(density[d], tree, edgeSet);
                  attempts++;
               } while (!checkConnected(tree, edgeSet) && attempts < maxAttempts);
               if (attempts == maxAttempts) {
                  printf("\tCould not generate a valid edge set\n\n");
               } else {
                  printf("\tFinished\n\n");
               }
*/