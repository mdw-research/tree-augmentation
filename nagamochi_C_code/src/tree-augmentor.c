#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <sys/resource.h>
#include "../include/tree-generator.h"
#include "../include/tree-helper.h"
#include "../include/tree-greedy.h"
#include "../include/graph.h"
#include "../include/int-list.h"
#include "../include/list.h"
#include "../include/nagamochi.h"
#include "../include/blossom.h"
#include "../include/lemma7.h"


//TODO
//hashmap in children()
// merge_vertices breaks parent array. can only merge_path.
//case 3 and case 4 may leave f' edges uncovered. store these edges for later and see if they are covered at the end


void run_matching_test(){
  char *match_text = "28 2\n28 1\n1 3\n3 4\n4 5\n5 6\n2 6\n3 8\n8 7\n9 10\n10 11\n9 8\n9 11\n14 15\n16 17\n14 13\n16 13\n13 12\n12 11\n17 18\n15 19\n18 19\n6 25\n25 24\n24 23\n23 20\n24 22\n22 21\n21 20\n20 19\n5 26\n26 27";

  graph *match_test = graph_create_text(match_text, 28);
  int_ls* verts = NULL;
  for(int i = 1; i<=28; i++)
    verts = ls_add(verts,i);
  edge_ls* matchting = blossom_algorithm(match_test, verts);
  printf("matching: "); print_edge_ls(matchting);
  if(l_size(matchting) == 13){
    printf("\nthis is a maximum matching\n");
  }
  else{
    printf("\nthis is not a maximum matching\n");
  }
}


int main(int argc, char *argv[])
{
  srand(time(0));

  char *t_text = "1 14\n1 11\n2 14\n3 15\n4 13\n4 10\n5 11\n5 8\n5 7\n6 7\n7 6\n7 5\n8 5\n9 15\n9 12\n10 4\n11 16\n11 15\n11 5\n11 1\n12 9\n13 16\n13 4\n14 2\n14 1\n15 11\n15 9\n15 3\n16 13\n16 11";
  char *g_text = "1 14\n1 13\n1 11\n1 8\n1 7\n1 6\n1 5\n1 4\n2 15\n2 12\n2 11\n2 10\n2 9\n2 8\n2 7\n2 5\n2 3\n3 16\n3 15\n3 14\n3 13\n3 12\n3 11\n3 10\n3 7\n3 2\n4 15\n4 13\n4 11\n4 10\n4 9\n4 8\n4 1\n5 13\n5 10\n5 9\n5 8\n5 2\n5 1\n6 15\n6 13\n6 12\n6 11\n6 7\n6 1\n7 16\n7 15\n7 12\n7 9\n7 8\n7 6\n7 3\n7 2\n7 1\n8 15\n8 14\n8 12\n8 11\n8 9\n8 7\n8 5\n8 4\n8 2\n8 1\n9 16\n9 14\n9 8\n9 7\n9 5\n9 4\n9 2\n10 15\n10 12\n10 5\n10 4\n10 3\n10 2\n11 15\n11 13\n11 8\n11 6\n11 4\n11 3\n11 2\n11 1\n12 16\n12 15\n12 14\n12 10\n12 8\n12 7\n12 6\n12 3\n12 2\n13 16\n13 11\n13 6\n13 5\n13 4\n13 3\n13 1\n14 16\n14 15\n14 12\n14 9\n14 8\n14 3\n14 1\n15 16\n15 14\n15 12\n15 11\n15 10\n15 8\n15 7\n15 6\n15 4\n15 3\n15 2\n16 15\n16 14\n16 13\n16 12\n16 9\n16 7\n16 3";
  int size = 17; //size of the tree and graph above.
  //create tree and graph from text above
  //graph *t = graph_create_text(t_text, size); 
  //graph *g = graph_create_text(g_text, size);

  while(1){
    //create tree and graph
    graph* t = randomForestTree(16); int rt = 1; set_root(t, rt);
    graph* g = createEdgeSet(25, t);

    //copy t and g to cover
    graph* tt = normal_copy(t); set_root(tt,1);
    graph* gg = normal_copy(g);

    //copy t and g, so that the original graph can be printed later.
    graph* ttt = normal_copy(t); set_root(tt,1);
    graph* ggg = normal_copy(g);

    //solve t and g
    nagamochi(g,t,.1);

    // print retained edges
    print_edge(g->retain,1); 

    // use retained edges to cover copies
    for(edge* e = g->retain; e; e= e->next){ 
      int u = e->thisVertex;
      int v = e->otherVertex;
      retain_merge_trim(gg,tt,u,v);
    }

    int v_count = ls_size(children(t,1));

    if(v_count > 0){
      printf("copy was not covered\n");
      printf("gg: \n"); graph_print_all(gg); printf("\n\n");
      printf("gg: \n"); graph_print_all(gg); printf("\n\n");

      printf("retained in g: "); print_edge(g->retain,1);

      printf("gg: \n"); graph_print_all(gg); printf("\n\n");
      printf("tt: \n"); graph_print_all(tt); printf("\n\n");

      printf("original graphs:");
      printf("t:\n"); graph_print(ttt); printf("\n\n");
      printf("g:\n"); graph_print(ggg); printf("\n\n");
      while(1);
    }
  }

  return 0;
}