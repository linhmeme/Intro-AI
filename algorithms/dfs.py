def dfs_with_steps(G, orig_node, dest_node):
    stack = [orig_node]
    visited = set()
    came_from = {}
    visited_nodes = []
    edges = []

    while stack:
        current = stack.pop()
        if current in visited:
            continue

        visited.add(current)
        visited_nodes.append(current)

        if current == dest_node:
            break

        for neighbor in reversed(list(G.neighbors(current))):  # Đảo ngược để duyệt đúng thứ tự
            if neighbor not in visited:
                stack.append(neighbor)
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
        path = []  # Không tìm thấy đường đi

    return path, visited_nodes, edges
