import networkx as nx
import matplotlib.pyplot as plt

# Create a graph
G = nx.Graph()

# Add nodes
G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

# Define lists of edges for different styles
black_edges =  [(0, 1), (0, 6), (1, 2), (1, 5), (1, 7), (2, 3), (2, 4), (2, 8), (6, 9)]
dotted_edges =  [(0, 2), (0, 5), (1, 6), (6, 5), (6, 8), (7, 5), (3, 8), (3, 4), (4, 8), (8, 9)]

# Add edges to the graph
G.add_edges_from(black_edges)
G.add_edges_from(dotted_edges)

# Create a subgraph for the black edges (tree)
tree = nx.Graph()
tree.add_edges_from(black_edges)

# Get positions for all nodes using the spring layout for the tree
pos = nx.spring_layout(tree, seed=42)  # Use a seed for reproducibility

# Add positions for any remaining nodes in G that are not in the tree
remaining_nodes = set(G.nodes) - set(tree.nodes)
if remaining_nodes:
    pos.update(nx.spring_layout(G.subgraph(remaining_nodes), pos=pos, seed=42))

# Draw the nodes
nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=700)

# Draw the edges with different styles
nx.draw_networkx_edges(G, pos, edgelist=black_edges, edge_color='black')
nx.draw_networkx_edges(G, pos, edgelist=dotted_edges, edge_color='black', style='dotted')

# Draw the labels
nx.draw_networkx_labels(G, pos, font_size=20, font_color='black')

# Show the plot
plt.title("NetworkX Graph with Different Edge Styles")
plt.show()