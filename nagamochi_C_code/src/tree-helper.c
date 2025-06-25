#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../include/graph.h"

/* prints an adjacency matrix
   n is the number of nodes in the tree
   tree is the adjacency matrix of size n x n */
void printTreeAdjMat(int n, int tree[][n]) {
   for(int i=0; i<n; i++) {
      for(int j=0; j<n; j++) {
        printf("%d ",tree[i][j]);
      }
      printf("\n");
   }
}

/* prints an adjacency matrix with formatting
   n is the number of nodes in the tree
   tree is the adjacency matrix of size n x n */
void printTreeAdjMatWithPadding(int n, int tree[][n], int padding) {
   for(int i=0; i<n; i++) {
      for(int j=0; j<n; j++) {
        printf("%0*d ", padding ,tree[i][j]);
      }
      printf("\n");
   }
}

int vertexCover(int min, int n, int tree[][n], int r, int cover[n], int vertex[n])
{
   //if(cur>=min)
   //   return -1;
   if(r>n){
      return min;
   }
    for(int i=0; i<n; i++){ //checks if this set covers
      for(int j=i+1; j<n; j++){
         if(tree[i][j]==1 && (cover[i]==0&&cover[j]==0)){ //if it doesn't, return max int (i think)
            return 2147483647;
         }
      }
    }
    int cur=0;
    for(int i=0; i<n; i++){
      if(cover[i]==1){
         cur=cur+vertex[i];
      }
    }
    if(cur<min){
      min=cur;
    }
   cover[r]=0;
   cur=vertexCover(min, n, tree, r+1, cover, vertex);
   if(cur<min){
      min=cur;
   }
   cover[r]=1;
   cur=vertexCover(min, n, tree, r+1, cover, vertex);
   if(cur<min){
      min=cur;
   }
   return cur;
}
int treeCover(int n, int tree[][n], int v,int stor[n][2], int covered, int parent[n], int vertex[n]){
   int leaf=1;
   for(int i=0; i<n; i++){
      if(tree[v][i]==1 && i!=parent[v]){
         leaf=0;
      }
   }
   if(leaf==1){                    //node doesn't have any new edge
       return covered*vertex[v];
   }
   else if(stor[v][covered]!=-1){      //already calculated
       return stor[v][covered];
   }
   int sum = 0;
   for(int i=0; i<n; i++){
       int u= tree[v][i];
       if(i!=parent[v]&& i!=v && u==1){             //not a parent
           parent[i]=v;
           if(covered==0){                 //not guarded, must set a watchman
               sum = sum + treeCover(n,tree,i,stor,1,parent,vertex);
           }
           else{
               int f1=treeCover(n,tree,i,stor,1,parent,vertex);//guarded, check both
               int f2=treeCover(n,tree,i,stor,0,parent,vertex);
               if(f1<f2){
                  sum=sum+f1;
               }
               else{
                  sum=sum+f2;
               }
         }
      }
   }
   stor[v][covered] = sum + covered*vertex[v];
    //printf("\n Stor: %d, v: %d, cover: %d \n", stor[v][covered],v,covered);
   return stor[v][covered];
}
void printMinCover(int n, int tree[][n], int vertex[n]){
      int parent[n];
      int stor[n][2];
      for(int i=0; i<n; i++){
         stor[i][0]=-1;
         stor[i][1]=-1;
         parent[i]=-1;
      }
      int minCover1=treeCover(n, tree, 0, stor, 1,parent, vertex);
      int minCover0=treeCover(n, tree, 0, stor, 0,parent, vertex);
      int cover=0;
      if(minCover1<minCover0){
         cover=minCover1;
      }
      else{
         cover=minCover0;
      }
      printf("\n Size of Vertex cover: %d \n", cover);
}

//to find and print minimum vertex cover
void printVertexCover(int n, int tree[][n], int vertex[n]) {
   int cover[n];
   for(int i=0; i<n; i++){
      cover[i]=1;
   }
   printf("\n Size of Vertex cover: %d \n", vertexCover(2147483647, n, tree, 0, cover, vertex) );
}

//to generate random vertex weights from 1 to max
void genVertexWeights(int n, int vertex[n], int max){
   for(int i=0; i<n; i++){
      vertex[i]= 1+(rand() % (max - 1 + 1));
   }
}
//to generate Latex for the plot
void genPlot(int numAlgorithms, int size, int timeSize, double times[][timeSize], int treeSize[]){
	FILE *fp;
	char typeName[20];
	fp=fopen("results/plots.txt", "w+");
	for(int treetype=1; treetype<=6; treetype++){
			switch(treetype) {
		      case 1:
		         strcpy(typeName, "Random Forest Graph");
		         break;
		      case 2:
		         strcpy(typeName, "Linear Tree");
		         break;
		      case 3:
		      	strcpy(typeName, "Star Tree");
		         break;
		      case 4:
		      	strcpy(typeName, "Starlike Tree");
		         break;
		      case 5:
		      	strcpy(typeName, "Caterpillar Tree");
		         break;
		      case 6:
		      	strcpy(typeName, "Lobster Tree");
		         break;
		      default:
		         printf("Error, invalid type\n");
		         break;
		   }
		fprintf(fp,"\\begin{figure} \n");
		fprintf(fp,"\\begin{tikzpicture} \n");
		fprintf(fp,"\\begin{axis}[ \n");
		fprintf(fp,"xlabel={n}, \n");
		fprintf(fp,"ylabel={time(s)}, \n");
		fprintf(fp,"xmin=100, xmax=10000,  \n");
		fprintf(fp,"ymin=0, ymax=1.1,\n");
		fprintf(fp,"ymajorgrids=true, \n");
		fprintf(fp,"xmajorgrids=true, \n");
		fprintf(fp,"grid style=dashed, \n");
		fprintf(fp,"legend style={at={(0.0,.91)},anchor=west} \n");
		fprintf(fp,"] \n");
		fprintf(fp,"\\addplot[blue, mark=diamond*] table [x=a, y=e, col sep=comma] { \n");
		fprintf(fp,"a,e \n");
		for(int n=0; n<size; n++){
			fprintf(fp, "%d, %f \n",treeSize[n], times[treetype-1][numAlgorithms*n]);
		}
		fprintf(fp,"};\n");
		fprintf(fp,"\\addplot[red, mark=square*] table [x=a, y=i, col sep=comma] { \n");
		fprintf(fp,"a,i \n");
		for(int n=0; n<size; n++){
			fprintf(fp, "%d, %f \n", treeSize[n], times[treetype-1][numAlgorithms*n+1]);
		}
		fprintf(fp,"};\n");
		fprintf(fp,"\\legend{Unweighted Vertex Cover,Weighted Vertex Cover}\n");
		fprintf(fp,"\\end{axis} \n");
		fprintf(fp,"\\end{tikzpicture} \n");
		fprintf(fp,"\\caption{%s} \n", typeName);
		fprintf(fp,"\\end{figure} \n");
	}

	fclose(fp);

}

/* Generates random edge weights from 1 to max for edges in a edge matrix */
void genEdgeWeights(int n, int edges[][n], int edgeWeights[][n], int max) {
   for(int i = 0; i < n; i++) {
      for(int j = 0; j < n; j++) {
         if(i > j && edges[i][j] == 1) {
            edgeWeights[i][j] = 1 + (rand() % (max - 1 + 1));
            edgeWeights[j][i] = edgeWeights[i][j];
         }
      }
   }
}

/*
// Currently this creates an adjacency matrix of all possible edges for the tree
   //basically a worst-case scenario, need to make sure this is acceptable
void createEdgeSet(int n, graph* tree, graph* edgeSet) {
   for(int i = 0; i < n; i++) {
      for(int j = 0; j < n; j++) {
         if(i != j && !graph_is_edge(tree, i, j)) {
            graph_add_edge(edgeSet, i, j);
         }
      }
   }
}
*/

/* Copies originalMatrix to copiedMatrix */
void copyMatrix(int n, int originalMatrix[][n], int copyMatrix[][n]) {
   for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
         copyMatrix[i][j] = originalMatrix[i][j];
      }
   }
}

void createCompleteDirectedTree(int n, int completeDirectedGraph[][n]) {
   for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
         if(i != j) {
            completeDirectedGraph[i][j] = 1;
         } else {
            completeDirectedGraph[i][j] = 0;
         }
      }
   }
}

/* returns 0 if there exists a bridge in the graph, otherwise returns 1 */
int _checkBridgeConnected(int n, int v, graph* tree, graph* edges, int arrival[], int visited[], int parent, int* depPtr) {
  /* set the arrival of the current node */
  arrival[v] = ++(*depPtr);
  /* mark the node as visited */
  visited[v] = 1;
  /* keep track of the current arrival of this node to see if it back connects */
  int d = arrival[v];
  int bfs;
  /* we need to check all the edges coming out from our current node */
  for (int j = 0; j < n; j++) {
    if (graph_is_edge(tree, v, j) || graph_is_edge(edges, v, j)) {
      /* if we find an edge to a node that has not been visited, recurse on the node */
      if (visited[j] == 0) {
        bfs = _checkBridgeConnected(n, j, tree, edges, arrival, visited, v, depPtr);
        /* if we find a bridge we can return */
        if (bfs == 0) {
          return 0;
        }
        d = (d < bfs) ? d : bfs;
      /* if we find a node that has been visited and it is not the parent
         see if the edge is back connected */
      } else if (j != parent) {
        d = (d < arrival[j]) ? d : arrival[j];
      }
    }
  }
  /* if our current subtree at v is not back connected, there exists a bridge */
  if (d == arrival[v] && parent != -1) {
    return 0;
  }
  return d;
}

/* returns 1 if the graph is 2-edge connected, 0 otherwise */
int checkConnected(int n, graph* tree, graph* edges) {
  /* perform DFS on graph rooted at node 0
	   we need to make sure no bridges exist in our graph */
	int r = 0;
	int dep = 0;
	int* depPtr = &dep;
	int parent =-1;
	int arrival[n];
	int visited[n];
	for (int i = 0; i < n; i++) {
	  arrival[i] = 0;
	  visited[i] = 0;
	}
	int check = _checkBridgeConnected(n, r, tree, edges, arrival, visited, parent, depPtr);

	return (check > 0) ? check : 0;
}
