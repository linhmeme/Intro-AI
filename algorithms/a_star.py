import heapq
from geopy.distance import geodesic

def a_star_with_steps(G, orig_node, dest_node):
    queue = [(0, orig_node)]
    visited = set()
    came_from = {}
    costs = {orig_node: 0}
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
            edge_data = G[current][neighbor]
            edge_weight = edge_data.get("weight", 1)  # dùng mặc định là 1 nếu không có 'weight'
            new_cost = costs[current] + edge_weight

            heuristic = geodesic(
                (G.nodes[neighbor]["y"], G.nodes[neighbor]["x"]),
                (G.nodes[dest_node]["y"], G.nodes[dest_node]["x"])
            ).meters

            priority = new_cost + heuristic

            if neighbor not in costs or new_cost < costs[neighbor]:
                costs[neighbor] = new_cost
                heapq.heappush(queue, (priority, neighbor))
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
