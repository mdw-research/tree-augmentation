import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def boxPlot(filename, size):
    # Read data from the text file
    data = pd.read_csv(filename)

    # Define the types of trees and capitalize them
    tree_types = ['caterpillar', 'path', 'star', 'lobster', 'random', 'starlike']
    tree_types_capitalized = [tree_type.capitalize() for tree_type in tree_types]

    # Capitalize the tree names in the 'tree' column
    data[' tree'] = data[' tree'].str.strip().str.capitalize()

    # Find the index of the "randomized" column
    frederickson_idx = data.columns.get_loc(" randomized")

    # Define the columns to be plotted (columns to the right of "randomized")
    columns_to_plot = data.columns[frederickson_idx:]

    # Create a figure to hold all subplots
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(15, 10))
    fig.suptitle(f'Running Time for Each Tree Type (n = {size})')

    # Iterate over each type of tree
    for row_idx, tree_type in enumerate(tree_types_capitalized):
        # Filter data for the current tree type and size 'size'
        filtered_data = data[(data[' tree'] == tree_type) & (data[' size'] == size)]

        # Calculate subplot position
        row = row_idx // 3
        col = row_idx % 3

        # Iterate over each column to plot
        for algorithm_idx, column in enumerate(columns_to_plot):
            # Get data for the current column
            column_data = filtered_data[column]

            # Create box and whiskers plot for the current column
            axes[row, col].boxplot(column_data.dropna(), positions=[algorithm_idx + 1])

            # Mark the mean with an 'X' inside the box
            mean_value = np.mean(column_data)
            axes[row, col].scatter(algorithm_idx + 1, mean_value, color='r', marker='x', s=100)

        axes[row, col].set_title(tree_type)
        axes[row, col].set_ylabel('Runtime (s)')
        axes[row, col].set_xlabel('Algorithm')
        axes[row, col].set_xticks(range(1, len(columns_to_plot) + 1))
        axes[row, col].set_xticklabels([col.strip().capitalize() for col in columns_to_plot], rotation=45, ha='right')

    # Adjust layout with padding between subplots, increasing hspace for more vertical spacing
    plt.subplots_adjust(wspace=0.4, hspace=0.6)

    # Save the figure
    plt.savefig(f'{filename[:-4]}Boxplot{size}.png')

if __name__ == '__main__':
    boxPlot("time20240613-071754.txt", 1000)
    # boxPlot("results/20240429-113440/results20240429-113440.txt", 1000)
