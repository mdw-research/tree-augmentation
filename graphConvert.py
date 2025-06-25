pythonTree = [(0,3),(0,4),(4,1),(1,2)]
pythonGraph = [(2,0),(2,3)]

# Increment each vertex by 1
for i in range(len(pythonTree)):
    pythonTree[i] = (pythonTree[i][0]+1,pythonTree[i][1]+1)
for i in range(len(pythonGraph)):
    pythonGraph[i] = (pythonGraph[i][0]+1,pythonGraph[i][1]+1)

# Get size
sizeTree = []
for element in pythonTree:
    sizeTree.append(element[0])
    sizeTree.append(element[1])
size = max(sizeTree)+1

tText = "\""
gText = "\""

for i in range(len(pythonTree)):
    tText += str(pythonTree[i][0]) + " " + str(pythonTree[i][1])
    if i != len(pythonTree) - 1:
        tText += "\\n"
tText += "\""

for i in range(len(pythonGraph)):
    gText += str(pythonGraph[i][0]) + " " + str(pythonGraph[i][1])
    if i != len(pythonGraph) - 1:
        gText += "\\n"
gText += "\""


print(tText)
print(gText)
print("size = ", size)