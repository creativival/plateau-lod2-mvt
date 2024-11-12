from mapbox_vector_tile import decode
import os
import math
from .building import Building
# 必要なインポートを追加
from shapely.geometry import Polygon, MultiPolygon, LinearRing, Point


class BuildingDataLoader:
    vertex_count = 0
    simplified_vertex_count = 0
    all_building_count = 0
    rect_building_count = 0
    not_rect_building_count = 0

    @staticmethod
    def load_buildings(z, x, y):
        # PBFファイルのパス
        pbf_file = f'{z}/{x}/{y}.pbf'

        # ファイルの存在確認
        if not os.path.isfile(pbf_file):
            print(f"PBF file not found: {pbf_file}")
            return []

        building_list = []

        # PBFファイルの読み込み
        with open(pbf_file, 'rb') as f:
            data = f.read()
            tile = decode(data)

        # レイヤーの取得
        buildings = tile.get('bldg', {})
        if not buildings:
            print("The 'bldg' layer is not available in this tile.")
            return []

        for feature in buildings.get('features', []):
            id_value = feature.get('id', None)
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            coordinates = geometry.get('coordinates', [])
            height = properties.get('z') or properties.get('height') or 0

            # coordinates の深さを取得
            depth = BuildingDataLoader.get_list_depth(coordinates)

            # Buildingインスタンスの作成
            if depth == 3:
                building = BuildingDataLoader.instancing_building(id_value, coordinates, height)
                building_list.append(building)
            elif depth == 4:
                # print(f"depth 4 coordinates len: {len(coordinates)}")
                for coords in coordinates:
                    building = BuildingDataLoader.instancing_building(id_value, coords, height)
                    building_list.append(building)
            else:
                print(f"Unexpected coordinates depth ({depth}) for building ID {id_value}")
                # building = Building(id_value, height=height)

        return building_list

    @staticmethod
    def instancing_building(id_value, coordinates, height):
        building = Building(id_value, coordinates=coordinates, height=height)
        simplified_coords, centroid, radius, rect_params = \
            BuildingDataLoader.process_coordinates(building.coordinates)
        building.simplified_coordinates = simplified_coords
        building.centroid = centroid
        building.bounding_circle_radius = radius
        # 長方形パラメータを設定
        building.rect_width, building.rect_height, building.rect_angle = rect_params

        return building

    @staticmethod
    def process_coordinates(coords):
        # シェイプリーのポリゴンを作成
        linear_ring = LinearRing(coords[0])
        polygon = Polygon(linear_ring)

        # 簡略化の度合いを設定（値が大きいほど頂点数が減少）
        tolerance = 30  # 必要に応じて調整

        # ポリゴンの簡略化
        simplified_polygon = polygon
        # simplified_polygon = polygon.simplify(tolerance, preserve_topology=True)
        # simplified_polygon = polygon.convex_hull

        # 簡略化した座標を取得
        simplified_coords = [list(simplified_polygon.exterior.coords)]

        # 重心の計算
        centroid = simplified_polygon.centroid
        centroid_coords = (centroid.x, centroid.y)

        # 包含円の半径を計算
        all_points = [Point(pt) for pt in simplified_polygon.exterior.coords]
        radius = BuildingDataLoader.calculate_bounding_circle_radius(all_points, centroid)

        # 元の頂点数と簡略化後の頂点数を記録
        # print("元の頂点数:", len(polygon.exterior.coords))
        # print("簡略化後の頂点数:", len(simplified_polygon.exterior.coords))
        BuildingDataLoader.vertex_count += len(polygon.exterior.coords)
        BuildingDataLoader.simplified_vertex_count += len(simplified_polygon.exterior.coords)

        # 四辺形の場合、長方形パラメータを計算
        rect_width = rect_height = rect_angle = None
        if len(simplified_polygon.exterior.coords) == 5:  # 最後の点が閉じるため4つの頂点
            min_rect = simplified_polygon.minimum_rotated_rectangle
            rect_coords = list(min_rect.exterior.coords)
            # 最小外接長方形の4つの頂点
            rect_points = rect_coords[:-1]  # 最後の閉じる点を除く

            # 2点間の距離を計算して幅と高さを決定
            edge_lengths = []
            for i in range(4):
                p1 = rect_points[i]
                p2 = rect_points[(i + 1) % 4]
                edge_length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
                edge_lengths.append(edge_length)

            # 幅と高さを長さの小さい順に割り当て
            sorted_lengths = sorted(edge_lengths)
            rect_width, rect_height = sorted_lengths[:2]

            # 回転角度を計算（最初のエッジの角度）
            p1, p2 = rect_points[0], rect_points[1]
            delta_x = p2[0] - p1[0]
            delta_y = p2[1] - p1[1]
            rect_angle = math.degrees(math.atan2(delta_y, delta_x))

            BuildingDataLoader.rect_building_count += 1
        else:
            BuildingDataLoader.not_rect_building_count += 1

        BuildingDataLoader.all_building_count += 1

        return simplified_coords, centroid_coords, radius, (rect_width, rect_height, rect_angle)

    @staticmethod
    def calculate_centroid(points):
        # ポイントの集合から重心を計算
        x_coords = [point.x for point in points]
        y_coords = [point.y for point in points]
        centroid_x = sum(x_coords) / len(x_coords)
        centroid_y = sum(y_coords) / len(y_coords)
        return Point(centroid_x, centroid_y)

    @staticmethod
    def calculate_bounding_circle_radius(points, centroid):
        # 重心から各ポイントまでの距離の最大値を取得
        distances = [centroid.distance(point) for point in points]
        return max(distances)

    @staticmethod
    def get_list_depth(lst):
        """
        リストのネストの深さを取得します。
        空リストの場合は1とします。
        """
        if isinstance(lst, list):
            if not lst:  # 空リスト
                return 1
            return 1 + max(BuildingDataLoader.get_list_depth(item) for item in lst)
        else:
            return 0

