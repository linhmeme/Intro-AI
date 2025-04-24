from .dijkstra import dijkstra_with_steps
from .a_star import a_star_with_steps
from .bfs import bfs_with_steps
from .bidirectional_dijkstra import bidirectional_dijkstra_with_steps

def find_shortest_path(G, orig_node, dest_node, algorithm):
    if algorithm == "dijkstra":
        path, visited, edges = dijkstra_with_steps(G, orig_node, dest_node)
        return path, visited, edges, [], []

    elif algorithm == "a_star":
        path, visited, edges = a_star_with_steps(G, orig_node, dest_node)
        return path, visited, edges, [], [] 

    elif algorithm == "bidirectional_dijkstra":
        path, visited_forward, edges_forward, visited_backward, edges_backward = bidirectional_dijkstra_with_steps(G, orig_node, dest_node)
        return path, visited_forward, edges_forward, visited_backward, edges_backward  

    elif algorithm == "bfs":
        path, visited, edges = bfs_with_steps(G, orig_node, dest_node)
        return path, visited, edges, [], []
    
    else:
        return None
