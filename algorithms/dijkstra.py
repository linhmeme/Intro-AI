import heapq

def dijkstra_with_steps(G, orig_node, dest_node):
    queue = [(0, orig_node)]
    visited = set()
    came_from = {}
    costs = {orig_node: 0}
    visited_nodes = []
    edges = []

    while queue:
        cost, current = heapq.heappop(queue)
        if current in visited:
            continue

        visited.add(current)
        visited_nodes.append(current)

        if current == dest_node:
            break

        for neighbor in G.neighbors(current):
            edge_weight = G[current][neighbor].get("weight", 1)
            new_cost = cost + edge_weight

            if neighbor not in costs or new_cost < costs[neighbor]:
                costs[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor))
                came_from[neighbor] = current
                edges.append((current, neighbor))

    path = []
    node = dest_node
    while node in came_from:
        path.append(node)
        node = came_from[node]
    path.append(orig_node)
    path.reverse()

    return path, visited_nodes, edges
