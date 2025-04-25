import osmnx as ox
place_name = "Thịnh Quang, Đống Đa, Hà Nội, Việt Nam"
graph = ox.graph_from_place(place_name, network_type ='drive')
ox.save_graphml(graph, "thinh_quang.graphml")
ox.plot_graph(graph)