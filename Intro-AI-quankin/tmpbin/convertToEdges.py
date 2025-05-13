# import json
# from geopy.distance import geodesic

# def compute_length(coords):
#     return sum(geodesic((a[1], a[0]), (b[1], b[0])).meters for a, b in zip(coords[:-1], coords[1:]))

# def convertToEdges(input_file="C:/Users/pc11w/OneDrive/Tài liệu/intro ai/data/geojson/roads.geojson", output_file="C:/Users/pc11w/OneDrive/Tài liệu/intro ai/data/geojson/edges.geojson"):
#     with open(input_file, 'r', encoding='utf-8') as f:
#         data = json.load(f)

#     edge_features = []

#     for feature in data['features']:
#         geom_type = feature['geometry']['type']
#         coords_group = feature['geometry']['coordinates']
#         props = feature.get('properties', {})
#         name = props.get('name', 'unknown')
#         oneway = props.get('oneway', 'no')
#         condition = props.get('condition', 'normal')

#         # MultiLineString hoặc LineString đều xử lý tương tự
#         if geom_type == "LineString":
#             coords_group = [coords_group]

#         for coords in coords_group:
#             for i in range(len(coords) - 1):
#                 p1, p2 = coords[i], coords[i+1]
#                 length = geodesic((p1[1], p1[0]), (p2[1], p2[0])).meters

#                 edge = {
#                     "type": "Feature",
#                     "geometry": {
#                         "type": "LineString",
#                         "coordinates": [p1, p2]
#                     },
#                     "properties": {
#                         "from": p1,
#                         "to": p2,
#                         "name": name,
#                         "length": round(length, 2),
#                         "condition": condition,
#                         "oneway": oneway
#                     }
#                 }
#                 edge_features.append(edge)

#                 if oneway != "yes":
#                     reverse_edge = {
#                         "type": "Feature",
#                         "geometry": {
#                             "type": "LineString",
#                             "coordinates": [p2, p1]
#                         },
#                         "properties": {
#                             "from": p2,
#                             "to": p1,
#                             "name": name,
#                             "length": round(length, 2),
#                             "condition": condition,
#                             "oneway": oneway
#                         }
#                     }
#                     edge_features.append(reverse_edge)

#     result = {
#         "type": "FeatureCollection",
#         "features": edge_features
#     }

#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(result, f, ensure_ascii=False, indent=2)

#     print(f"✅ Đã xuất {len(edge_features)} edges vào '{output_file}'")

# if __name__ == "__main__":
#     convertToEdges("C:/Users/pc11w/OneDrive/Tài liệu/intro ai/data/geojson/roads.geojson", "C:/Users/pc11w/OneDrive/Tài liệu/intro ai/data/geojson/edges.geojson")
