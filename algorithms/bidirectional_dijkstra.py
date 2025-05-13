import heapq

def bidirectional_dijkstra_with_steps(G, orig_node, dest_node):
    forward_visited = set()
    backward_visited = set()
    forward_edges = []
    backward_edges = []

    forward_came_from = {}
    backward_came_from = {}

    forward_heap = [(0, orig_node)]
    backward_heap = [(0, dest_node)]

    forward_g_score = {orig_node: 0}
    backward_g_score = {dest_node: 0}

    meeting_node = None

    while forward_heap and backward_heap:
        # Forward direction
        if forward_heap:
            _, current = heapq.heappop(forward_heap)
            forward_visited.add(current)

            if current in backward_visited:
                meeting_node = current
                break

            for neighbor in G.neighbors(current):
                edge_weight = G[current][neighbor].get('weight', 1)
                new_cost = forward_g_score[current] + edge_weight
                if neighbor not in forward_g_score or new_cost < forward_g_score[neighbor]:
                    forward_g_score[neighbor] = new_cost
                    heapq.heappush(forward_heap, (new_cost, neighbor))
                    forward_came_from[neighbor] = current
                    forward_edges.append((current, neighbor))

        # Backward direction
        if backward_heap:
            _, current = heapq.heappop(backward_heap)
            backward_visited.add(current)

            if current in forward_visited:
                meeting_node = current
                break

            for neighbor in G.neighbors(current):
                edge_weight = G[current][neighbor].get('weight', 1)
                new_cost = backward_g_score[current] + edge_weight
                if neighbor not in backward_g_score or new_cost < backward_g_score[neighbor]:
                    backward_g_score[neighbor] = new_cost
                    heapq.heappush(backward_heap, (new_cost, neighbor))
                    backward_came_from[neighbor] = current
                    backward_edges.append((current, neighbor))

    # Reconstruct path
    path = []
    if meeting_node:
        node = meeting_node
        while node in forward_came_from:
            path.append(node)
            node = forward_came_from[node]
        path.append(orig_node)
        path.reverse()

        node = meeting_node
        while node in backward_came_from:
            node = backward_came_from[node]
            path.append(node)

    return path, list(forward_visited), forward_edges, list(backward_visited), backward_edges
