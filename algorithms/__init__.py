from .dijkstra import dijkstra_with_steps
from .a_star import a_star_with_steps
from .bfs import bfs_with_steps
from .dfs import dfs_with_steps
from .bidirectional_dijkstra import bidirectional_dijkstra_with_steps
from .greedy import greedy_best_first_search  

# Ánh xạ tên thuật toán với hàm tương ứng
ALGORITHMS = {
    "dijkstra": dijkstra_with_steps,
    "a_star": a_star_with_steps,
    "bfs": bfs_with_steps,
    "dfs": dfs_with_steps,
    "greedy": greedy_best_first_search
}

def find_shortest_path(G, orig_node, dest_node, vehicle, algorithm):
    if algorithm == "bidirectional_dijkstra":
        path, visited_f, edges_f, visited_b, edges_b = bidirectional_dijkstra_with_steps(G, orig_node, dest_node)
        return path, visited_f, edges_f, visited_b, edges_b

    algo_fn = ALGORITHMS.get(algorithm)
    if algo_fn:
        path, visited, edges = algo_fn(G, orig_node, dest_node)
        return path, visited, edges, [], []

    return None
