from collections import deque

def bfs_with_steps(G, orig_node, dest_node):
    queue = deque([orig_node]) 
    visited = set()
    came_from = {} 
    visited_nodes = [] 
    edges = [] 

    while queue:
        current = queue.popleft() 

        if current in visited:
            continue

        visited.add(current)
        visited_nodes.append(current)

        if current == dest_node:
            break 

        for neighbor in G.neighbors(current):
            if neighbor not in visited:
                queue.append(neighbor)
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
