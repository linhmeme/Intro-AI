import heapq
from geopy.distance import geodesic

def greedy_best_first_search(G, orig_node, dest_node):
    def heuristic(node):
        return geodesic(
            (G.nodes[node]["y"], G.nodes[node]["x"]),
            (G.nodes[dest_node]["y"], G.nodes[dest_node]["x"])
        ).meters

    queue = [(heuristic(orig_node), orig_node)]
    visited = set()
    came_from = {}
    visited_nodes = []
    edges = []

    while queue:
        _, current = heapq.heappop(queue)
        if current in visited:
            continue

        visited.add(current)
        visited_nodes.append(current)

        if current == dest_node:
            break

        for neighbor in G.neighbors(current):
            if neighbor not in visited:
                heapq.heappush(queue, (heuristic(neighbor), neighbor))
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    edges.append((current, neighbor))

    # reconstruct path
    path = []
    node = dest_node
    while node in came_from:
        path.append(node)
        node = came_from[node]
    if node == orig_node:
        path.append(orig_node)
        path.reverse()
    else:
        path = []  # No path found

    return path, visited_nodes, edges
