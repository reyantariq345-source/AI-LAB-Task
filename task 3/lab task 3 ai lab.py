#BFS code:
graph = {
    'A': ['B', 'C'], 'B': ['D', 'E'],
    'C': ['F'], 'D': ['G'], 'E': ['G'],
    'F': ['G'], 'G': []
}

def bfs(start, goal):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for child in graph[node]:
                queue.append(path + [child])
    return None

print("BFS path:", bfs('A', 'G'))

#DFs code:
def dfs(node, goal, path):
    if node == goal:
        return path
    for child in graph[node]:
        if child not in path:
            answer = DFs (child, goal, path + [child])
            if answer:
                return answer
    return None

print("DFS path:", dfs('A', 'G', ['A']))

#DLs code

def dls(node, goal, limit, path):
    if node == goal:
        return path
    if limit == 0:
        return "CUTOFF"

    cutoff_happened = False
    for child in graph[node]:
        if child not in path:
            result = dls(child, goal, limit - 1, path + [child])
            if isinstance(result, list):
                return result
            if result == "CUTOFF":
                cutoff_happened = True

    if cutoff_happened:
        return "CUTOFF"
    return "FAILURE"

    #IDDFs code:
    for limit in range(1, 5):
    result = dls('A', 'G', limit, ['A'])
    print("Limit", limit, ":", result)
    if isinstance(result, list):
        break
#UCS code:
import heapq

weighted_graph = {
    'A': [('B', 1), ('C', 2)],
    'B': [('D', 2), ('E', 5), ('C', 1)],
    'C': [('F', 2)], 'D': [('G', 8)],
    'E': [('G', 1)], 'F': [('G', 2)], 'G': []
}

def ucs(start, goal):
    frontier = [(0, start, [start])]
    best_cost = {}
    while frontier:
        cost, node, path = heapq.heappop(frontier)
        if node in best_cost and best_cost[node] <= cost:
            continue
        best_cost[node] = cost
        if node == goal:
            return path, cost
        for child, edge_cost in weighted_graph[node]:
            if child not in best_cost:
                heapq.heappush(frontier, (cost + edge_cost, child, path + [child]))
    return None, None

print("UCS result:", ucs('A', 'G'))


