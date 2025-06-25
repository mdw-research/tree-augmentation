import datetime
import os
import time
import tracemalloc
import treegenerator as tg
import frederickson
import exact
import randomized
import even
import quality_boxplots as bp
import nagamochi

def main():
    # Create a directory named "results" if it doesn't exist
    if not os.path.exists("results"):
        os.makedirs("results")
    date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    result_dir_path = os.path.join("results", date)
    os.makedirs(result_dir_path)
    result_dir = result_dir_path

    with open(os.path.join(result_dir, f"results{date}.txt"), "w") as file:
        file.write(f"test, size, density, tree, frederickson, randomized, exact, even, nagamochi\n")
    with open(os.path.join(result_dir, f"time{date}.txt"), "w") as file:
        file.write(f"test, size, density, tree, frederickson, randomized, exact, even, nagamochi\n")
    with open(os.path.join(result_dir, f"memory{date}.txt"), "w") as file:
        file.write(f"test, size, density, tree, frederickson, randomized, exact, even, nagamochi\n")

    sizes = [100, 1000, 10000]
    densities = [0.1, 0.5, 0.8]
    trees = ["path", "star", "starlike", "caterpillar", "lobster", "random"]
    treeFunc = [tg.path_tree, tg.star_tree, tg.starlike_tree, tg.caterpillar_tree, tg.lobster_tree, tg.random_tree]
    iterations = range(3)
    for s in sizes:
        for d in densities:
            for idx, tree in enumerate(trees):
                if s == sizes[0] and d == densities[0] and tree == trees[0]:
                    iterations = range(4)
                else:
                    iterations = range(3)

                for i in iterations:

                    with open(os.path.join(result_dir, f"results{date}.txt"), "a") as file:
                        file.write(f"{i+1}, {s}, {d}, {tree}")
                    
                    T = treeFunc[idx](s)
                    L = tg.generate_links(T, d)
                    
                    tracemalloc.start()
                    st = time.time()
                    fredericksonNumLinks = frederickson.frederickson(T, L)
                    fredericksonTime = time.time() - st
                    current, fredericksonMem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()

                    with open(os.path.join(result_dir, f"results{date}.txt"), "a") as file:
                        file.write(f", {fredericksonNumLinks}")

                    tracemalloc.start()
                    st = time.time()
                    randomizedNumLinks = randomized.randomized(T, L)
                    randomizedTime = time.time() - st
                    current, randomizedMem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()

                    with open(os.path.join(result_dir, f"results{date}.txt"), "a") as file:
                        file.write(f", {randomizedNumLinks}")

                    exactNumLinks, exactMem, exactTime = exact.cutlp(T, L)
                    
                    with open(os.path.join(result_dir, f"results{date}.txt"), "a") as file:
                        file.write(f", {exactNumLinks}")

                    tracemalloc.start()
                    st = time.time()
                    evenNumLinks = even.even(T, L)
                    evenTime = time.time() - st
                    current, evenMem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    
                    with open(os.path.join(result_dir, f"results{date}.txt"), "a") as file:
                        file.write(f", {evenNumLinks}\n")

                    with open(os.path.join(result_dir, f"time{date}.txt"), "a") as file:
                        file.write(f"{i+1}, {s}, {d}, {tree}, {fredericksonTime}, {randomizedTime}, {exactTime}, {evenTime}\n")
                    with open(os.path.join(result_dir, f"memory{date}.txt"), "a") as file:
                        file.write(f"{i+1}, {s}, {d}, {tree}, {fredericksonMem}, {randomizedMem}, {exactMem}, {evenMem}\n")
                    
    bp.boxPlot(f"results/{date}/results{date}.txt", 5)


if __name__ == "__main__":
    main()
